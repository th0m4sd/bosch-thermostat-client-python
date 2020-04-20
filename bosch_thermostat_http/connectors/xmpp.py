"""XMPP Connector to talk to bosch."""
import logging
import json
# import slixmpp
import asyncio

import aioxmpp
from bosch_thermostat_http.exceptions import DeviceException


_LOGGER = logging.getLogger(__name__)


class XMPPBaseConnector:
    serial_number = None
    access_key = None

    jid = None
    _from = None
    _to = None
    client = None

    event = None
    container = {}

    def __init__(self, serial_number, loop, access_key, encryption, host="wa2-mz36-qrmzh6.bosch.de", sasl_mech="DIGEST-MD5"):
        """
        :param serial_number:
        :param access_key:
        :param password:
        :param host:
        :param sasl_mech:
        """
        self.serial_number = serial_number
        self.loop = loop
        self._encryption = encryption

        identifier = serial_number + "@" + host
        self._from = self._rrc_contact_prefix + identifier
        self._to = self.jid(self._rrc_gateway_prefix + identifier)
        self._jid = self.jid(self._from)
        self.xmppclient = aioxmpp.PresenceManagedClient(
            self._jid,
            aioxmpp.make_security_layer(self._accesskey_prefix + access_key)
        )
        self.stop_signal = None
        message_dispatcher = self.xmppclient.summon(
            aioxmpp.dispatcher.SimpleMessageDispatcher
        )
        message_dispatcher.register_callback(
            aioxmpp.MessageType.NORMAL,
            None,
            self.message_received,
        )
        message_dispatcher.register_callback(
            aioxmpp.MessageType.CHAT,
            None,
            self.message_received,
        )
        self._seqno = 1

    def jid(self, _from):
        return aioxmpp.JID.fromstr(_from)

    def message_received(self, msg):
        if not msg.body:
            self.stop_signal.set()
            print("NIE MA BODY!")
            return
        body = msg.body.lookup(
            [aioxmpp.structs.LanguageRange.fromstr("*")]
        ).split("\n")
        if "HTTP/1.0 200" in body[0]:
            data = self._encryption.json_encrypt(body[-1:][0])
            self.stop_signal.result = data
        # elif body[0] == "HTTP/1.0 400 Bad Request":
        #     print("ERROR")
        self.stop_signal.set()

    async def get(self, uri, timeout=10):
        # self.event = Event()
        data = None
        async with self.xmppclient.connected():
            self.stop_signal = asyncio.Event()
            await self.xmppclient.send(self.build_message(uri))
            await self.stop_signal.wait()
            if hasattr(self.stop_signal, 'result'):
                data = self.stop_signal.result
            else:
                raise DeviceException(f"Error requesting data from {uri}")
                # print("WIADOMOSC nie pobrana %s", uri)
        return data

    def put(self, uri, data, timeout=10):
        data = data if isinstance(data, str) else json.dumps(data, separators=(',', ':'))
        encrypted_data = self.encrypt(data).decode("utf8")
        body = "\r".join([
            'PUT %s HTTP/1.1' % uri,
            'Content-Type: application/json',
            'Content-Length: %i' % len(encrypted_data),
            'User-Agent: NefitEasy\r',
            encrypted_data
        ])
        self.event = Event()
        self.client.add_event_handler("message", self.message)
        self.send(body)
        self.event.wait(timeout=timeout)
        self.client.del_event_handler("message", self.message)

    def send(self, body):
        # this horrible piece of code breaks xml syntax but does actually work...
        body = body.replace("\r", "&#13;\n")
        message = self.client.make_message(mto=self._to, mfrom=self._from, mbody=body)
        message['lang'] = None
        str_data = tostring(message.xml, xmlns=message.stream.default_ns,
                            stream=message.stream,
                            top_level=True)
        str_data = str_data.replace("&amp;#13;", "&#13;")