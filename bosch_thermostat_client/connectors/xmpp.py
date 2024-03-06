"""XMPP Connector to talk to bosch."""
import logging
from typing import (
    Awaitable,
    List,
)
import json
import re

from slixmpp import ClientXMPP, Iq, stanza
from slixmpp.exceptions import IqError, IqTimeout
from slixmpp.plugins.base import BasePlugin
from slixmpp.xmlstream.handler import Callback
from slixmpp.xmlstream.matcher import StanzaPath
import asyncio
from contextlib import AsyncExitStack
from bosch_thermostat_client.exceptions import (
    DeviceException,
    MsgException,
    EncryptionException,
)
from bosch_thermostat_client.const import (
    GET,
    PUT,
    REQUEST_TIMEOUT,
    BODY_400,
    WRONG_ENCRYPTION,
    ACCESS_KEY,
)

_LOGGER = logging.getLogger(__name__)


class BoschXMPPClient(ClientXMPP):
    def __init__(self, jid, to_jid, password, *args, **kwargs):
        self.loop = asyncio.get_event_loop()
        self._to_jid = to_jid
        super().__init__(jid, password, *args, **kwargs)

        self.register_plugin('xep_0030')  # Service Discovery
        self.register_plugin('xep_0199')  # XMPP Ping


        # self.query_handler.register()
        self.connected_event = asyncio.Event()

        self.add_event_handler("session_start", self.start)
        self.add_event_handler("message", self.message)
        self.register_handler(Callback('Query Request', StanzaPath('iq@type=get/query'), self.handle_query_request))

        self.session_started = False
        self.received_message = None
        self.connect(use_ssl=False, force_starttls=False, disable_starttls=True)
        # self.do_it()
        print("aa")

    # def do_it(self):
    #     tasks: List[Awaitable] = [asyncio.Task(asyncio.sleep(0.1))]
    #     tasks.append(self.disconnected)
    #     self.loop.run_until_complete(asyncio.wait(tasks))

    def handle_query_request(self, iq):
        if iq['query']['xmlns'] == 'com.bosch.tt.buderus.controlng':
            response = Iq()
            response['type'] = 'result'
            response['id'] = iq['id']
            response['to'] = iq['from']
            response['query']['xmlns'] = 'com.bosch.tt.buderus.controlng'
            response['query']['name'] = '3.6.0'
            response['query']['version'] = '3.6.0'
            response['query']['os'] = ''
            self.xmpp.send(response)

    async def start(self, event):
        print("start")
        self.send_presence()
        self.get_roster()

        self.session_started = True
        self.connected_event.set()
        # self.process()
        print("oki")

    # async def async_connect(self):
    #     loop = asyncio.get_event_loop()
        
    #     loop.run_until_complete(self.connected_event)

    def message(self, msg):
        print("msg", msg)
        if msg['type'] in ('chat', 'normal'):
            self.received_message = msg['body']

    async def send_and_await_response(self, message: str):
        try:
            print("session started", self.session_started)
            print("start!", message)
            print("ehh")
            if not self.session_started:
                print("waiting for session")
                await asyncio.wait_for(self.connected_event.wait(), timeout=10)
                print("jest session")
            _LOGGER.error("O co chodzi %s", message)
            response = self.send_message(mto=self._to_jid, mbody=message, mtype='chat')
            print("resp", response)
            return response
        except IqError as e:
            _LOGGER.error("Error sending message: %s", e)
            return None
        except IqTimeout:
            _LOGGER.error("Timeout sending message")
            return None
        except Exception as e:
            print("error", e)
            pass

    def get_received_message(self):
        return self.received_message


class XMPPBaseConnector:
    no_verify = False

    def __init__(self, host, encryption, **kwargs):
        """
        :param host: aka serial number
        :param password:
        """
        self.serial_number = host
        self._encryption = encryption
        self._lock = asyncio.Lock()

        identifier = self.serial_number + "@" + self.xmpp_host
        self._from = self._rrc_contact_prefix + identifier

        self._to = self._rrc_gateway_prefix + identifier
        self._password = self._accesskey_prefix + kwargs.get(ACCESS_KEY)
        print("init")
        # self.client = BoschXMPPClient(jid=self._from, to_jid=self._to, password=self._password)
        self.client = ClientXMPP(jid=self._from, password=self._password)
        self.client.register_plugin('xep_0030')  # Service Discovery
        self.client.register_plugin('xep_0199')  # XMPP Ping
        self.client.add_event_handler("session_start", self.start)
        self.client.add_event_handler("message", self.main_listener)
        self.client.register_handler(Callback('Query Request', StanzaPath('iq@type=get/query'), self.handle_query_request))
        self.connected_event = asyncio.Event()
        self.session_started = False
        self.received_message = None

        self._st = AsyncExitStack()
        self.listeners = set()
        self._xmppstream = None

    def handle_query_request(self, iq):
        if iq['query']['xmlns'] == 'com.bosch.tt.buderus.controlng':
            response = Iq()
            response['type'] = 'result'
            response['id'] = iq['id']
            response['to'] = iq['from']
            response['query']['xmlns'] = 'com.bosch.tt.buderus.controlng'
            response['query']['name'] = '3.6.0'
            response['query']['version'] = '3.6.0'
            response['query']['os'] = ''
            self.client.send(response)

    async def start(self, event):
        print("START!")
        self.client.send_presence()
        self.client.get_roster()
        self.session_started = True
        self.connected_event.set()

    @property
    def encryption_key(self):
        return self._encryption.key

    def _build_message(self, method, path, data=None):
        pass


    async def get(self, path):
        _LOGGER.debug("Sending GET request to %s by %s", path, id(self))
        data = await self._request(method=GET, path=path)
        _LOGGER.debug("Response to GET request %s: %s", path, json.dumps(data))
        if not data:
            raise DeviceException(f"Error requesting data from {path}")
        return data

    async def put(self, path, value):
        _LOGGER.debug("Sending PUT request to %s with value %s", path, value)
        data = await self._request(
            method=PUT,
            encrypted_msg=self._encryption.encrypt(json.dumps({"value": value})),
            path=path,
            timeout=10,
        )
        if data:
            return True

    async def close(self, force):
        await asyncio.wait_for(self._st.aclose(), 10)

    async def _request(self, method, path, encrypted_msg=None, timeout=REQUEST_TIMEOUT):
        data = None
        try:
            if not self.session_started:
                print("connecting!")
                self.client.connect(use_ssl=False, force_starttls=False, disable_starttls=True)
                print("waiting")
                await asyncio.wait_for(self.connected_event.wait(), timeout=10)
                print("dalej")
        except asyncio.TimeoutError:
            print("nie dzaial")
            _LOGGER.error(
                "Can't connect to XMPP server!. Check your network connection or credentials!"
            )
            return None
        print("lock aquire")
        await self._lock.acquire()
        msg_to_send = self._build_message(
            method=method, path=path, data=encrypted_msg
        )
        try:
            future = asyncio.Future()
            print("future")

            def listener(recv_body, http_response):
                if future.done() or future.cancelled():
                    _LOGGER.debug(
                        "Future is already done. If it happens too often that it might be a bug. Report it."
                    )
                    return
                if method == PUT and http_response == "HTTP/1.0 204 No Content":
                    future.set_result(True)
                if recv_body == BODY_400:
                    future.set_exception(MsgException("400 HTTP Error"))
                elif recv_body is None and http_response == WRONG_ENCRYPTION:
                    future.set_exception(EncryptionException("Can't decrypt for %s" % path))
                elif method == GET and recv_body.get("id") in path:
                    try:
                        future.set_result(recv_body)
                    except (asyncio.InvalidStateError) as err:
                        _LOGGER.error(
                            "If you see this log please attach it to your issue/send it on Discord. Err message: %s. Recv body: %s, Path: %s",
                            err,
                            json.dumps(recv_body),
                            path,
                        )
                        self._xmppstream = None
                        pass
            try:
                print("WYSYLAMY")
                self.listeners.add(listener)
                print("START!@")
                print("message, send", msg_to_send)
                self.client.send_message(mto=self._to, mbody=msg_to_send, mtype='chat')
                print("wyslane!!")
                data = await asyncio.wait_for(future, timeout)
            except (asyncio.TimeoutError, MsgException):
                _LOGGER.info("Msg exception for %s", path)
            except (EncryptionException) as err:
                _LOGGER.warn(err)
                raise EncryptionException(err)
            except (asyncio.InvalidStateError) as err:
                _LOGGER.error("Unknown error occured. Please check logs. %s", err)
            finally:
                self.listeners.remove(listener)
        finally:
            self._lock.release()
            return data

    def main_listener(self, msg):
        print("boddy", msg['type'], msg['body'])
        if msg['type'] not in ('normal', 'chat'):
            return
        body = msg['body']
        if not body:
            return
            
        def notify_error(body, response):
            if len(self.listeners) == 1:
                for listener in self.listeners:
                    listener(body, response)
                    break

        try:
            body_arr = body.split(
                "\n"
            )
        except AttributeError:
            return
        http_response = body_arr[0]
        if re.match(r"HTTP/1.[0-1] 20*", http_response):
            try:
                decrypted_body = self._encryption.json_decrypt(body_arr[-1:][0])
            except EncryptionException:
                notify_error(body=None, response=WRONG_ENCRYPTION)
            else:
                for listener in self.listeners:
                    print("mam", decrypted_body, http_response)
                    listener(decrypted_body, http_response)
            return
        if re.match(r"HTTP/1.[0-1] 40*", http_response):
            _LOGGER.info(f"400 HTTP Error - {body_arr}")
            notify_error(body=BODY_400, response=http_response)
