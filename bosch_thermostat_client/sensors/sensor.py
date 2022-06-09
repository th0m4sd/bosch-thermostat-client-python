from __future__ import annotations
from bosch_thermostat_client.helper import BoschSingleEntity, DeviceClassEntity
from bosch_thermostat_client.const import RESULT, URI, TYPE, REGULAR, VALUE
from bosch_thermostat_client.const.ivt import INVALID


class Sensor(BoschSingleEntity, DeviceClassEntity):
    """Single sensor object."""

    def __init__(
        self,
        attr_id: str,
        path: str,
        device_class: str = None,
        state_class: str = None,
        kind: str = REGULAR,
        **kwargs
    ) -> None:
        """
        Single sensor init.

        :param dics requests: { GET: get function, SUBMIT: submit function}
        :param str path: path to retrieve data from sensor.
        """
        BoschSingleEntity.__init__(self, path=path, attr_id=attr_id, **kwargs)
        DeviceClassEntity.__init__(
            self, device_class=device_class, state_class=state_class
        )
        self._kind = kind
        self._device_class = device_class
        self._state_class = state_class
        self._data = {attr_id: {RESULT: {}, URI: path, TYPE: kind}}

    @property
    def kind(self) -> str:
        return self._kind

    @property
    def state(self) -> str:
        """Retrieve state of the circuit."""
        result = self._data[self.attr_id].get(RESULT)
        if result:
            return result.get(VALUE, INVALID)
        return "unavailable"
