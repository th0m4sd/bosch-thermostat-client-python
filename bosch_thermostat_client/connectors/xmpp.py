"""XMPP Connector to talk to bosch."""
import logging
import json
import re

import asyncio

import aioxmpp
from bosch_thermostat_client.exceptions import DeviceException
from bosch_thermostat_client.const import GET, PUT


_LOGGER = logging.getLogger(__name__)


class XMPPBaseConnector:

    def __init__(self, host, loop, access_key, encryption):
        """
        :param host: aka serial number
        :param access_key:
        :param password:
        :param host:
        :param sasl_mech:
        """
        self.serial_number = host
        self.loop = loop
        self._encryption = encryption
        self._request_timeout = 10
        self._lock = asyncio.Lock()
        self.msg_event = None
        self.msg_fut = None

        identifier = self.serial_number + "@" + self.xmpp_host
        self._from = self._rrc_contact_prefix + identifier
        self._to = self.jid(self._rrc_gateway_prefix + identifier)
        self._jid = self.jid(self._from)
        self.xmppclient = aioxmpp.PresenceManagedClient(
            self._jid,
            aioxmpp.make_security_layer(self._accesskey_prefix + access_key)
        )
        self.message_dispatcher = self.xmppclient.summon(
            aioxmpp.dispatcher.SimpleMessageDispatcher
        )
        self.register_callbacks()
        _LOGGER.debug("Done __INIT__ function")

    @property
    def encryption_key(self):
        return self._encryption.key

    def register_callbacks(self):
        self.message_dispatcher.register_callback(
            aioxmpp.MessageType.NORMAL,
            None,
            self.message_received,
        )
        self.message_dispatcher.register_callback(
            aioxmpp.MessageType.CHAT,
            None,
            self.message_received,
        )

    def unregister_callbacks(self):
        self.message_dispatcher.unregister_callback(
            aioxmpp.MessageType.NORMAL,
            None
        )
        self.message_dispatcher.unregister_callback(
            aioxmpp.MessageType.CHAT,
            None
        )

    def jid(self, _from):
        return aioxmpp.JID.fromstr(_from)

    def _build_message(self, method, path, data=None):
        pass

    def message_received(self, msg):
        if not msg.body:
            self.stop_signal.set()
            return
        body = msg.body.lookup(
            [aioxmpp.structs.LanguageRange.fromstr("*")]
        ).split("\n")
        if re.match(r"HTTP/1.[0-1] 40*", body[0]):
            _LOGGER.error(f"400 HTTP Error - {body}")
            self.msg_event.data = None
        elif re.match(r"HTTP/1.[0-1] 20*", body[0]):
            body = self._encryption.json_encrypt(body[-1:][0])
            if body == "{}":
                _LOGGER.error(f"Wrong body {body}")
                self.msg_fut.set_exception(DeviceException(""))
            else:
                self.msg_fut.set_result(body)

    async def get(self, path):
        _LOGGER.debug("Sending GET request to %s by %s", path, id(self))
        done = None
        async with self._lock:
            _LOGGER.debug("Running ASYNC with self.xmppclient.connected")
            try:
                print("===============START=================")
                async with self.xmppclient.connected():
                    self.msg_fut = asyncio.Future(loop=self.loop)
                    msg = self._build_message(method=GET, path=path)
                    await self.xmppclient.send(msg)
                    done = await asyncio.wait_for(self.msg_fut, self._request_timeout) 
                    if done:
                        print("DONE ====>", done)
                        return done
                print("==============STOP===============")
            except (asyncio.TimeoutError, asyncio.InvalidStateError, DeviceException):
                print("==========OUT==========")
                raise DeviceException(f"Error requesting data from {path}")

    async def put(self, path, value):
        data = self._encryption.encrypt(json.dumps({"value": value}, separators=(',', ':')))
        _LOGGER.debug("Sending PUT request to %s", path)
        async with self._lock:
            async with self.xmppclient.connected():
                self.msg_fut = asyncio.Future(loop=self.loop)
                await self.xmppclient.send(self._build_message(
                    method=PUT,
                    path=path,
                    data=data))
                await asyncio.wait_for(self.msg_event.wait(), self._request_timeout)
                if hasattr(self.msg_event, 'data'):
                    data = self.msg_event.data
                self.msg_event = None
                if data:
                    return True
        return False