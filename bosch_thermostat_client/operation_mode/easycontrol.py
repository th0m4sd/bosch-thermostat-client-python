from .base import OperationModeHelper
from bosch_thermostat_client.const import SETPOINT


class EasyControlOperationModeHelper(OperationModeHelper):
    @property
    def available_modes(self):
        """Get Bosch operations modes."""
        return ["clock", "manual"]

    def temp_setpoint_read(self, mode=None):
        """Check which temp property to use. Key READ or WRITE"""
        mode = self.current_mode if not mode else mode
        return self._mode_to_setpoint.get(mode, {}).get(SETPOINT)