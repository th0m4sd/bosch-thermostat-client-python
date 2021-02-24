"""Retrieve standard data."""
import logging
import json
import os

from bosch_thermostat_client.const import DEFAULT
from bosch_thermostat_client.const.nefit import NEFIT
from bosch_thermostat_client.const.ivt import CAN, NSC_ICOM_GATEWAY, RC300_RC200

_LOGGER = logging.getLogger(__name__)

MAINPATH = os.path.join(os.path.dirname(__file__))

FILENAME = os.path.join(MAINPATH, "db.json")
DEVICE_TYPES = {
    RC300_RC200: "rc300_rc200.json",
    DEFAULT: "default.json",
    CAN: "can.json",
    NEFIT: "nefit.json",
    NSC_ICOM_GATEWAY: "nsc_icom_gateway.json",
}


def open_json(file):
    """Open json file."""
    with open(file, "r") as db_file:
        datastore = json.load(db_file)
        return datastore
    return None


def get_initial_db(device_type):
    filename = os.path.join(MAINPATH, f"db_{device_type}.json")
    """Get initial db. Same for all devices."""
    return open_json(filename)


def get_db_of_firmware(device_type, firmware_version):
    """Get db of specific device."""
    filename = DEVICE_TYPES[device_type]
    filepath = os.path.join(MAINPATH, filename)
    _LOGGER.debug("Attempt to load database from file %s", filepath)
    _db = open_json(filepath)
    if _db:
        if firmware_version in _db:
            return _db[firmware_version]
    return None


def get_custom_db(firmware_version, _db):
    """Get db of device if yours doesn't exists."""
    if _db:
        if firmware_version in _db:
            return _db[firmware_version]
    return None


def get_ivt_errors():
    """Get error codes of IVT devices."""
    return open_json(os.path.join(MAINPATH, "errorcodes_ivt.json"))
