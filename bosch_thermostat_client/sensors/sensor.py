from bosch_thermostat_client.helper import BoschSingleEntity
from bosch_thermostat_client.const import RESULT, URI, TYPE, REGULAR, VALUE
from bosch_thermostat_client.const.ivt import INVALID


class Sensor(BoschSingleEntity):
    """Single sensor object."""

    def __init__(
        self,
        connector,
        attr_id,
        name,
        path,
        device_class=None,
        state_class=None,
        kind=REGULAR,
    ):
        """
        Single sensor init.

        :param dics requests: { GET: get function, SUBMIT: submit function}
        :param str name: name of the sensors
        :param str path: path to retrieve data from sensor.
        """
        super().__init__(name, connector, attr_id, path)
        self._kind = kind
        self._device_class = device_class
        self._state_class = state_class
        self._data = {attr_id: {RESULT: {}, URI: path, TYPE: kind}}

    @property
    def kind(self):
        return self._kind

    @property
    def device_class(self):
        return self._device_class

    @property
    def state_class(self):
        return self._state_class

    @property
    def state(self):
        """Retrieve state of the circuit."""
        result = self._data[self.attr_id].get(RESULT)
        if result:
            return result.get(VALUE, INVALID)
        return "unavailable"
