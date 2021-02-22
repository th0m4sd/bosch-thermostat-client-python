"""XMPP Connector to talk to bosch."""
import logging
import json
import re

import asyncio

import aioxmpp
from bosch_thermostat_client.exceptions import DeviceException, MsgException
from bosch_thermostat_client.const import GET, PUT


_LOGGER = logging.getLogger(__name__)
REQUEST_TIMEOUT = 10


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
        self._lock = asyncio.Lock()
        self.msg_event = None
        self.msg_fut = None

        identifier = self.serial_number + "@" + self.xmpp_host
        self._from = self._rrc_contact_prefix + identifier
        self._to = self.jid(self._rrc_gateway_prefix + identifier)
        self._jid = self.jid(self._from)
        self.xmppclient = aioxmpp.PresenceManagedClient(
            self._jid, aioxmpp.make_security_layer(self._accesskey_prefix + access_key)
        )
        self.message_dispatcher = self.xmppclient.summon(
            aioxmpp.dispatcher.SimpleMessageDispatcher
        )
        self._get_future = asyncio.Future(loop=self.loop)
        self._put_future = asyncio.Future(loop=self.loop)
        self._msg_to_send = None
        self.register_callbacks()
        asyncio.create_task(self._xmpp_connect())

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

    def jid(self, _from):
        return aioxmpp.JID.fromstr(_from)

    def _build_message(self, method, path, data=None):
        pass

    def message_received(self, msg):
        if not msg.body:
            return
        body = msg.body.lookup([aioxmpp.structs.LanguageRange.fromstr("*")]).split("\n")
        if re.match(r"HTTP/1.[0-1] 40*", body[0]):
            _LOGGER.error(f"400 HTTP Error - {body}")
            self.msg_fut.set_exception(MsgException("400 HTTP Error"))
        elif re.match(r"HTTP/1.[0-1] 20*", body[0]):
            body = self._encryption.json_encrypt(body[-1:][0])
            if body == "{}":
                _LOGGER.error(f"Wrong body {body}")
                self.msg_fut.set_exception(MsgException(f"Wrong body {body}"))
            else:
                self.msg_fut.set_result(body)

    async def get(self, path):
        _LOGGER.debug("Sending GET request to %s by %s", path, id(self))
        data = await self._request(msg=self._build_message(method=GET, path=path))
        if not data:
            raise DeviceException(f"Error requesting data from {path}")
        return data

    async def put(self, path, value):
        _LOGGER.debug("Sending PUT request to %s", path)
        data = await self._request(
            msg=self._build_message(
                method=PUT,
                path=path,
                data=self._encryption.encrypt(
                    json.dumps({"value": value}, separators=(",", ":"))
                ),
            )
        )
        if data:
            return True

    async def _request(self, msg):
        done = None
        async with self._lock:
            self.msg_fut = asyncio.Future(loop=self.loop)
            try:
                self._req_future.set_result(msg)
                async with self.xmppclient.connected():
                    await self.xmppclient.send(msg)
                    done = await asyncio.wait_for(self.msg_fut, REQUEST_TIMEOUT)
            except (asyncio.TimeoutError, MsgException):
                _LOGGER.warn("Msg exception.")
            else:
                return done

    async def _xmpp_connect(self):
        try:
            async with self.xmppclient.connected() as stream:
                while True:
                    done, pending = await asyncio.wait(self._req_future)
                    if self._req_future in done:
                        msg = self._req_future.result()
                        if not msg:
                            break
                        await self.xmppclient.send(msg)
                        self._req_future = asyncio.Future(loop=self.loop)
        finally:
            self._req_future.cancel()
