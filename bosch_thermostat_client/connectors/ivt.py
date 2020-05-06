"""XMPP Connector to talk to bosch."""
import aioxmpp
from bosch_thermostat_client.const import PUT, GET, USER_AGENT, CONTENT_TYPE, APP_JSON
from bosch_thermostat_client.const.ivt import TELEHEATER
from .xmpp import XMPPBaseConnector


class IVTXMPPConnector(XMPPBaseConnector):
    _accesskey_prefix = 'C6u9jPue_'
    _rrc_contact_prefix = 'contact_'
    _rrc_gateway_prefix = 'gateway_'
    xmpp_host = "wa2-mz36-qrmzh6.bosch.de"

    def __init__(self, host, loop, access_key, encryption):
        """IVTConnector constructor

        Args:
            host (str): serialnumber of target
            loop (loop): asyncio loop
            access_key (str): access key to bosch
            encryption (obj): Encryption object
        """
        self._seqno = 1
        super().__init__(host, loop, access_key, encryption)

    def _build_message(self, method, path, data=None):
        msg = aioxmpp.stanza.Message(
            to=self._to,
            type_=aioxmpp.MessageType.CHAT,
        )
        if method == GET:
            body = "\r\r".join([
                f'GET {path} HTTP/1.1',
                f'{USER_AGENT}: {TELEHEATER}',
                '\r\r'
            ])
        elif method == PUT and data:
            body = "\r\r".join([
                f'PUT {path} HTTP/1.1',
                f'{USER_AGENT}: {TELEHEATER}',
                f'{CONTENT_TYPE}: {APP_JSON}',
                f'Content-Length: {len(data)}',
                '',
                data.decode('utf-8'),
                '\r\r'
            ])
        msg.body[None] = body
        self._seqno += 1
        return msg
