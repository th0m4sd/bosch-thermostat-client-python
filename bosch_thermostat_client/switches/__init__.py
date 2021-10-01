"""
Switches of Bosch thermostat.
"""
from bosch_thermostat_client.const import ID, NAME, TYPE, NUMBER
from bosch_thermostat_client.const.ivt import ALLOWED_VALUES
from bosch_thermostat_client.const.easycontrol import USED, BOOLEAN
from bosch_thermostat_client.helper import BoschEntities

from bosch_thermostat_client.exceptions import DeviceException
from .switch import Switch
from .boolean import BooleanSwitch
from .number import NumberSwitch


class Switches(BoschEntities):
    """Sensors object containing multiple Sensor objects."""

    def __init__(self, connector, uri_prefix=None):
        """
        Initialize sensors.

        :param dict requests: { GET: get function, SUBMIT: submit function}
        """
        self._connector = connector
        super().__init__(connector.get)
        self._items = {}
        self._number_switches = {}
        self._uri_prefix = uri_prefix

    async def initialize(self, switches):
        if not switches:
            return
        for switch_id, switch in switches.items():
            try:
                uri = (
                    f"{self._uri_prefix}/{switch[ID]}"
                    if self._uri_prefix
                    else switch[ID]
                )
                retrieved = await self._get(uri)
                if ALLOWED_VALUES in retrieved:
                    self._items[switch_id] = Switch(
                        self._connector, switch_id, switch[NAME], uri, retrieved
                    )
                elif switch.get(TYPE, False) == BOOLEAN and retrieved.get(USED, False):
                    self._items[switch_id] = BooleanSwitch(
                        self._connector, switch_id, switch[NAME], uri, retrieved
                    )
                elif switch.get(TYPE, False) == NUMBER:
                    self._number_switches[switch_id] = NumberSwitch(
                        self._connector, switch_id, switch[NAME], uri, retrieved
                    )
            except DeviceException:
                pass

    def __iter__(self):
        return iter(self._items.values())

    @property
    def switches(self):
        """Get switches list."""
        return self.get_items().values()

    @property
    def number_switches(self):
        """Get number switches."""
        return self._number_switches.values()
