"""XMPP Connector to talk to bosch."""
import logging

import aioxmpp
from bosch_thermostat_client.const import PUT, GET, USER_AGENT, CONTENT_TYPE, APP_JSON
from .xmpp import XMPPBaseConnector

_LOGGER = logging.getLogger(__name__)

USERAGENT = "rrc2"


class EasycontrolConnector(XMPPBaseConnector):
    xmpp_host = "charlie.ticx.boschtt.net"
    _accesskey_prefix = "C42i9NNp_"
    _rrc_contact_prefix = "rrc2contact_"
    _rrc_gateway_prefix = "rrc2gateway_"

    def __init__(self, host, loop, access_key, encryption):
        self._seqno = 0
        super().__init__(host, loop, access_key, encryption)

    def _build_message(self, method, path, data=None):
        msg = aioxmpp.stanza.Message(
            to=self._to,
            type_=aioxmpp.MessageType.CHAT,
        )
        if method == GET:
            body = "\n".join(
                [
                    f"GET {path} HTTP/1.1",
                    f"{USER_AGENT}: {USERAGENT}",
                    f"Seq-No: {self._seqno}",
                    "\n",
                ]
            )
        elif method == PUT and data:
            body = "\r".join(
                [
                    f"PUT {path} HTTP/1.1",
                    f"{USER_AGENT}: {USERAGENT}",
                    f"{CONTENT_TYPE}: {APP_JSON}",
                    f"Content-Length: {len(data)}",
                    "",
                    data.decode("utf-8"),
                    "\r",
                ]
            )
        msg.body[None] = body
        self._seqno += 1
        return msg
