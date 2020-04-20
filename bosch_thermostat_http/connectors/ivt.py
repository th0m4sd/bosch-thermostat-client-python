"""XMPP Connector to talk to bosch."""
import aioxmpp
from bosch_thermostat_http.const import TELEHEATER as USERAGENT
from .xmpp import XMPPBaseConnector


class IVTConnector(XMPPBaseConnector):
    _accesskey_prefix = 'C6u9jPue_'
    _rrc_contact_prefix = 'contact_'
    _rrc_gateway_prefix = 'gateway_'
    _seqno = 1

    def build_message(self, uri):
        msg = aioxmpp.stanza.Message(
            to=self._to,
            type_=aioxmpp.MessageType.CHAT,
        )
        body = "\r\r".join([
            f'GET {uri} HTTP/1.1',
            f'User-Agent: {USERAGENT}',
            f'Seq-No: {self._seqno}',
            '\r\r'
        ])
        msg.body[None] = body
        self._seqno += 1
        return msg
