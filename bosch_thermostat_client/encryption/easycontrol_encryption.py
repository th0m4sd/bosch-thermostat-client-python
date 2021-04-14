"""Encryption logic of Bosch thermostat."""
from bosch_thermostat_client.const.easycontrol import MAGIC_EASYCONTROL

from .base_encryption import BaseEncryption


class EasycontrolEncryption(BaseEncryption):
    """Encryption class."""
    magic = MAGIC_EASYCONTROL
