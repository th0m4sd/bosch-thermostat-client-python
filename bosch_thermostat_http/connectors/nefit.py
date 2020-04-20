"""XMPP Connector to talk to bosch."""
import logging
import json
# import slixmpp
import asyncio
import signal

import aioxmpp
from bosch_thermostat_http.exceptions import DeviceException, ResponseException
from bosch_thermostat_http.const import NEFITEASY as USERAGENT
from .xmpp import XMPPBaseConnector

_LOGGER = logging.getLogger(__name__)


class NefitConnector(XMPPBaseConnector):
    _accesskey_prefix = 'Ct7ZR03b_'
    _rrc_contact_prefix = 'rrccontact_'
    _rrc_gateway_prefix = 'rrcgateway_'

    def build_message(self, uri):
        msg = aioxmpp.stanza.Message(
            to=self._to,
            type_=aioxmpp.MessageType.CHAT,
        )
        body = "\r\r".join([
            f'GET {uri} HTTP/1.1',
            f'User-Agent: {USERAGENT}',
            '\r\r'
        ])
        msg.body[None] = body
        return msg


    def session_start(self, event):
        """Callback handler for the session start.
        """
        self.send_presence()
        self.get_roster()
        self['xep_0280'].enable()
        self.connected_event.set()

    def disconnect(self):
        self.client.disconnect()


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
        return message.stream.send_raw(str_data)

    def encrypt(self, data):
        return self.encryption.encrypt(data)

    def decrypt(self, data):
        return self.encryption.decrypt(data)