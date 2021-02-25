from .http import HttpConnector
from .ivt import IVTXMPPConnector
from .nefit import NefitConnector
from .nefit2 import NefitConnector2

from bosch_thermostat_client.const.ivt import HTTP


def connector_ivt_chooser(session_type):
    return HttpConnector if session_type.upper() == HTTP else IVTXMPPConnector


__all__ = ["NefitConnector", "NefitConnector2", "IVTXMPPConnector", "HttpConnector"]
