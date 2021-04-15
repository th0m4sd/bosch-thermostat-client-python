from .base import EasycontrolCircuit
from bosch_thermostat_client.const import NAME, STATUS, MODE_TO_SETPOINT
from bosch_thermostat_client.const.easycontrol import TARGET_TEMP
from bosch_thermostat_client.operation_mode import EasyControlOperationModeHelper


class EasyZoneCircuit(EasycontrolCircuit):
    def __init__(self, connector, attr_id, db, _type, bus_type, current_date=None):
        super().__init__(connector, attr_id, db, _type, bus_type, current_date)
        self._op_mode = EasyControlOperationModeHelper(
            self.name, self._db.get(MODE_TO_SETPOINT)
        )

    @property
    def name(self):
        name = self.get_value(NAME)
        return name if name else super().name

    @property
    def schedule(self):
        """Easy control might not need schedule."""
        return None

    async def initialize(self):
        """Check each uri if return json with values."""
        await self.update_requested_key(STATUS)
        await self.update_requested_key(NAME)

    @property
    def target_temperature(self):
        """Get target temperature of Circtuit. Temporary or Room set point."""
        if self._op_mode.is_off:
            self._target_temp = 0
            return self._target_temp
        target_temp = self.get_value(TARGET_TEMP, 0)
        if target_temp > 0:
            self._target_temp = target_temp
            return self._target_temp
