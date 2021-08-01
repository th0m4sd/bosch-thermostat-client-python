"""
Switches of Bosch thermostat.
"""

from bosch_thermostat_client.const import (
    ID,
    NAME,
    RESULT,
    URI,
    TYPE,
    VALUE,
    REGULAR,
)
from bosch_thermostat_client.const.ivt import INVALID, ALLOWED_VALUES
from bosch_thermostat_client.const.easycontrol import TRUE, FALSE, USED, BOOLEAN
from bosch_thermostat_client.helper import (
    BoschSingleEntity,
    BoschEntities,
)

from bosch_thermostat_client.exceptions import DeviceException

ON_STATES = ["start", "on"]
OFF_STATES = ["stop", "off"]


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
            except DeviceException:
                pass

    def __iter__(self):
        return iter(self._items.values())

    @property
    def switches(self):
        """Get switches list."""
        return self.get_items().values()


class Switch(BoschSingleEntity):
    """Single switch object."""

    def __init__(self, connector, attr_id, name, path, result):
        """
        Single switch init.

        :param dics requests: { GET: get function, SUBMIT: submit function}
        :param str name: name of the switches
        :param str path: path to retrieve data from switch.
        :param str obj: result retrieved during initialization.
        """
        super().__init__(name, connector, attr_id, path)
        self._data = {attr_id: {RESULT: {}, URI: path, TYPE: REGULAR}}
        self.process_results(result, attr_id)

    async def turn_on(self):
        await self._turn_action(ON_STATES)

    async def turn_off(self):
        await self._turn_action(OFF_STATES)

    async def _turn_action(self, states):
        allowed = self.get_property(ALLOWED_VALUES)
        for state in states:
            if state in allowed:
                await self._connector.put(self._data[self.attr_id][URI], state)
                self._data[self.attr_id][RESULT][VALUE] = state
                break

    @property
    def state(self):
        """Retrieve state of the switch."""
        result = self._data[self.attr_id].get(RESULT)
        if result:
            value = result.get(VALUE, INVALID)
            return True if value in ON_STATES else False
        return False


class BooleanSwitch(BoschSingleEntity):
    """Single switch object."""

    def __init__(self, connector, attr_id, name, path, result):
        """
        Single switch init.

        :param dics requests: { GET: get function, SUBMIT: submit function}
        :param str name: name of the switches
        :param str path: path to retrieve data from switch.
        :param str obj: result retrieved during initialization.
        """
        super().__init__(name, connector, attr_id, path)
        self._data = {attr_id: {RESULT: {}, URI: path, TYPE: REGULAR}}
        self.process_results(result, attr_id)

    async def turn_on(self):
        if not self.state:
            await self._turn_action(TRUE)

    async def turn_off(self):
        if self.state:
            await self._turn_action(FALSE)

    async def _turn_action(self, action):
        await self._connector.put(self._data[self.attr_id][URI], action)
        self._data[self.attr_id][RESULT][VALUE] = action

    @property
    def state(self):
        """Retrieve state of the switch."""
        result = self._data[self.attr_id].get(RESULT)
        if result:
            return True if result.get(VALUE, INVALID) == TRUE else False
        return False
