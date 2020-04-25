from .circuit import Circuit
from bosch_thermostat_client.const import (
    STATUS,
    DEFAULT_MIN_TEMP,
    MIN_REF,
    DEFAULT_MAX_TEMP,
    MAX_REF,
)


class NefitCircuit(Circuit):
    @property
    def state(self):
        """Retrieve state of the circuit."""
        if self._state:
            return True if self.get_value(STATUS) else False

    @property
    def min_temp(self):
        """Retrieve minimum temperature."""
        if self._op_mode.is_off:
            return DEFAULT_MIN_TEMP
        else:
            return self.get_value(self._db[MIN_REF], DEFAULT_MIN_TEMP)

    @property
    def max_temp(self):
        """Retrieve maximum temperature."""
        if self._op_mode.is_off:
            return DEFAULT_MAX_TEMP
        else:
            return self.get_value(self._db[MAX_REF], DEFAULT_MAX_TEMP)

    @property
    def target_temperature(self):
        """Get target temperature of Circtuit. Temporary or Room set point."""
        print("IS OFF")
        print(self._op_mode.is_off)
        if self._op_mode.is_off:
            self._target_temp = 0
            return self._target_temp
        print(self._temp_setpoint)
        if self._temp_setpoint:
            target_temp = self.get_value(self._temp_setpoint, 0)
            if target_temp > 0:
                self._target_temp = target_temp
                return self._target_temp
