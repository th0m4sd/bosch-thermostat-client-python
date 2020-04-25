from .ivt_gateway import IVTGateway
from .nefit_gateway import NefitGateway
from bosch_thermostat_client.const.ivt import IVT


def gateway_chooser(device_type=IVT):
    return IVTGateway if device_type == IVT else NefitGateway
