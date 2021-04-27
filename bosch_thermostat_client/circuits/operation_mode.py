from bosch_thermostat_client.const import VALUE, SETPOINT, TYPE, AUTO, OFF, MANUAL
from bosch_thermostat_client.const.ivt import ALLOWED_VALUES


class OperationModeHelper:
    def __init__(self, name, mode_to_setpoint):
        self.name = name
        self._operation_mode = {}
        self._uri = False
        self._mode_to_setpoint = mode_to_setpoint

    def init_op_mode(self, operation_mode, uri):
        self._operation_mode = operation_mode
        self._uri = uri

    def set_new_operation_mode(self, value):
        self._operation_mode[VALUE] = value

    @property
    def uri(self):
        return self._uri

    @property
    def is_set(self):
        return self._uri

    @property
    def available_modes(self):
        """Get Bosch operations modes."""
        return self._operation_mode.get(ALLOWED_VALUES, {})

    def find_in_available_modes(self, modes):
        for mode in modes:
            if mode in self.available_modes:
                return mode

    @property
    def current_mode(self):
        """Retrieve current mode of Circuit."""
        return self._operation_mode.get(VALUE, None)

    def temp_setpoint(self, mode=None):
        """Check which temp property to use. Key READ or WRITE"""
        mode = self.current_mode if not mode else mode
        return self._mode_to_setpoint.get(mode, {}).get(SETPOINT)

    @property
    def mode_type(self):
        """Check if operation mode type is manual or auto."""
        return self._mode_to_setpoint.get(self.current_mode, {}).get(TYPE)

    @property
    def is_off(self):
        return self.mode_type == OFF

    @property
    def is_manual(self):
        return self.mode_type == MANUAL

    @property
    def is_auto(self):
        return self.mode_type == AUTO
