"""
Sensors of Bosch thermostat.
NotificationSensor uses error codes prepared by Hans Liss in his repo at
https://github.com/hansliss/regofetcher
"""

from bosch_thermostat_client.const import (
    ID,
    NAME,
    RESULT,
    URI,
    TYPE,
    REGULAR,
    SENSOR,
    VALUE,
    VALUES,
)
from bosch_thermostat_client.const.ivt import INVALID
from bosch_thermostat_client.db import get_ivt_errors
from .helper import BoschSingleEntity, BoschEntities


class Sensors(BoschEntities):
    """Sensors object containing multiple Sensor objects."""

    def __init__(self, connector, sensors=None, sensors_db=None, uri_prefix=None):
        """
        Initialize sensors.

        :param dict requests: { GET: get function, SUBMIT: submit function}
        """
        self._index = 0
        super().__init__(connector.get)
        self._items = {}
        for sensor_id in sensors:
            sensor = sensors_db.get(sensor_id)
            if sensor and sensor_id not in self._items:
                if sensor_id == "notifications":
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

    def __iter__(self):
        return iter(self._items.values())

    @property
    def sensors(self):
        """Get sensor list."""
        return self.get_items().values()


class Sensor(BoschSingleEntity):
    """Single sensor object."""

    def __init__(self, connector, attr_id, name, path):
        """
        Single sensor init.

        :param dics requests: { GET: get function, SUBMIT: submit function}
        :param str name: name of the sensors
        :param str path: path to retrieve data from sensor.
        """
        super().__init__(name, connector, attr_id, SENSOR, path)
        self._data = {attr_id: {RESULT: {}, URI: path, TYPE: REGULAR}}

    @property
    def state(self):
        """Retrieve state of the circuit."""
        result = self._data[self.attr_id].get(RESULT)
        if result:
            return result.get(VALUE, INVALID)
        return -1


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
