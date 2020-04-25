"""Sensors of Bosch thermostat."""
from bosch_thermostat_client.const import ID, NAME, RESULT, URI, TYPE, REGULAR, SENSOR, VALUE
from bosch_thermostat_client.const.ivt import INVALID
from .helper import BoschSingleEntity, BoschEntities


class Sensors(BoschEntities):
    """Sensors object containing multiple Sensor objects."""

    def __init__(self, connector, sensors=None, sensors_db=None):
        """
        Initialize sensors.

        :param dict requests: { GET: get function, SUBMIT: submit function}
        """
        super().__init__(connector.get)
        self._items = {}
        for sensor_id in sensors:
            sensor = sensors_db.get(sensor_id)
            if sensor and sensor_id not in self._items:
                self._items[sensor_id] = Sensor(
                    connector, sensor_id, sensor[NAME], sensor[ID]
                )

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
