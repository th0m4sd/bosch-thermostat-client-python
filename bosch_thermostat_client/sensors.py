"""
Sensors of Bosch thermostat.
NotificationSensor uses error codes prepared by Hans Liss in his repo at https://github.com/hansliss/regofetcher
"""

import logging
from bosch_thermostat_client.const import (
    ID,
    NAME,
    RESULT,
    URI,
    TYPE,
    REGULAR,
    VALUE,
    VALUES,
    INTERVAL,
    RECORDINGS,
    RECORDING,
    RECORDERDRES,
)
from datetime import datetime
from bosch_thermostat_client.const.ivt import INVALID
from bosch_thermostat_client.exceptions import DeviceException
from bosch_thermostat_client.db import get_ivt_errors
from .helper import BoschSingleEntity, BoschEntities

_LOGGER = logging.getLogger(__name__)
NOTIFICATIONS = "notifications"


class Sensors(BoschEntities):
    """Sensors object containing multiple Sensor objects."""

    def __init__(self, connector, sensors_db=None, uri_prefix=None):
        """
        Initialize sensors.

        :param dict requests: { GET: get function, SUBMIT: submit function}
        """
        self._index = 0
        self._connector = connector
        super().__init__(connector.get)
        self._items = {}
        for sensor_id, sensor in sensors_db.items():
            if sensor_id not in self._items:
                if sensor_id == NOTIFICATIONS:
                    self._items[sensor_id] = NotificationSensor(
                        connector,
                        sensor_id,
                        sensor[NAME],
                        f"{uri_prefix}/{sensor[ID]}" if uri_prefix else sensor[ID],
                    )
                else:
                    self._items[sensor_id] = Sensor(
                        connector,
                        sensor_id,
                        sensor[NAME],
                        f"{uri_prefix}/{sensor[ID]}" if uri_prefix else sensor[ID],
                    )

    async def initialize(self, recordings):
        """Initialize recording sensors."""
        found_recordings = []
        for record in recordings:
            found_recordings.extend(await self.retrieve_from_module(4, record))
        for rec in found_recordings:
            sensor_id = f'r{rec[RECORDERDRES][ID].split("/")[-1]}'
            if sensor_id not in self._items:
                self._items[sensor_id] = RecordingSensor(
                    connector=self._connector,
                    attr_id=sensor_id,
                    name=sensor_id,
                    path=rec[ID],
                )

    def __iter__(self):
        return iter(self._items.values())

    @property
    def sensors(self):
        """Get sensor list."""
        return self.get_items().values()


class Sensor(BoschSingleEntity):
    """Single sensor object."""

    @property
    def kind(self):
        return REGULAR

    def __init__(self, connector, attr_id, name, path):
        """
        Single sensor init.

        :param dics requests: { GET: get function, SUBMIT: submit function}
        :param str name: name of the sensors
        :param str path: path to retrieve data from sensor.
        """
        super().__init__(name, connector, attr_id, path)
        self._data = {attr_id: {RESULT: {}, URI: path, TYPE: self.kind}}

    @property
    def state(self):
        """Retrieve state of the circuit."""
        result = self._data[self.attr_id].get(RESULT)
        if result:
            return result.get(VALUE, INVALID)
        return -1


class RecordingSensor(Sensor):
    def __init__(self, connector, attr_id, name, path):
        super().__init__(connector=connector, attr_id=attr_id, name=name, path=path)

        def unit_chooser(uri):
            if "energy" in uri:
                return "kWh"
            if "temp" in uri:
                return "C"
            return None

        self._unit_of_measurement = unit_chooser(uri=path)

    @property
    def kind(self):
        return RECORDINGS

    @property
    def unit_of_measurement(self):
        return self._unit_of_measurement

    def process_results(self, result):
        """Convert multi-level json object to one level object."""
        self._data[self.attr_id]
        if result:
            for recording in reversed(result[RECORDING]):
                if recording["c"] == 0:
                    continue
                self._data[self.attr_id][RESULT][VALUE] = round(
                    (recording["y"] / recording["c"]), 1
                )
                return True

    @property
    def state(self):
        """Retrieve state of the record sensor."""
        return self._data[self.attr_id].get(RESULT, {}).get(VALUE)

    def build_uri(self):
        today = datetime.today().strftime("%Y-%m-%d")
        return f"{self._data[self.attr_id][URI]}?{INTERVAL}={today}"

    async def update(self):
        """Update info about Recording Sensor asynchronously."""
        try:
            result = await self._connector.get(self.build_uri())
            self.process_results(result)
        except DeviceException as err:
            _LOGGER.error(
                f"Can't update data for {self.name}. Trying uri: {self._data[URI]}. Error message: {err}"
            )
            self._extra_message = f"Can't update data. Error: {err}"


class NotificationSensor(Sensor):
    errorcodes = get_ivt_errors()

    def process_results(self, result, key=None, return_data=False):
        """Convert multi-level json object to one level object."""
        data = {RESULT: {}} if return_data else self._data[key]
        updated = False
        if result:
            vals = result.get(VALUES, [])
            if vals:
                data[RESULT] = {}
                for idx, val in enumerate(vals):
                    if "ccd" in val:
                        ccd = str(val["ccd"])
                        key_suffix = "" if idx == 0 else "_" + idx
                        data[RESULT][VALUE + key_suffix] = self.errorcodes[ccd]["title"]
                        data[RESULT]["errorCode" + key_suffix] = val["dcd"] + "-" + ccd
                        for key, description in self.errorcodes[ccd].items():
                            if isinstance(description, list):
                                for alternative in description:
                                    for altkey in alternative:
                                        data[RESULT][
                                            key + key_suffix + "_" + altkey
                                        ] = alternative[altkey]
                            else:
                                data[RESULT][key + key_suffix] = description
                    else:
                        data[RESULT] = {VALUE: val}
            else:
                data[RESULT] = {VALUE: "No notifications"}
            self._update_initialized = True
            updated = True
        else:
            data[RESULT] = {VALUE: "Unknown"}
        return data[RESULT] if return_data else updated

    @property
    def state(self):
        """Retrieve state of the circuit."""
        result = self._data[self.attr_id].get(RESULT)
        if VALUE in result:
            return result.get(VALUE, INVALID)
        return result
