import logging
from bosch_thermostat_client.const import (
    RESULT,
    URI,
    VALUE,
    INTERVAL,
    RECORDINGS,
    RECORDING,
    TEMP_CELSIUS,
    ENERGY_KILO_WATT_HOUR,
)
from .sensor import Sensor
from bosch_thermostat_client.exceptions import DeviceException

from datetime import datetime, timedelta

_LOGGER = logging.getLogger(__name__)


class RecordingSensor(Sensor):
    def __init__(self, path: str, **kwargs) -> None:
        super().__init__(path=path, **kwargs)

        def unit_chooser():
            if any(x in path.lower() for x in ["energy", "power"]):
                return ENERGY_KILO_WATT_HOUR
            if any(x in path.lower() for x in ["temp", "outdoor"]):
                return TEMP_CELSIUS
            return None

        self._unit_of_measurement = unit_chooser()

    @property
    def kind(self) -> str:
        return RECORDINGS

    @property
    def unit_of_measurement(self) -> str:
        return self._unit_of_measurement

    def process_results(self, result: dict, time: datetime) -> None:
        """Convert multi-level json object to one level object."""

        def get_last_full_hour() -> time:
            return time - timedelta(hours=1)

        if result and RECORDING in result:
            last_hour = get_last_full_hour()
            # recording = result[RECORDING][last_hour.hour - 1]
            self._data[self.attr_id][RESULT][VALUE] = []
            for idx, recording in enumerate(result[RECORDING]):
                if recording["c"] == 0:
                    continue
                self._data[self.attr_id][RESULT][VALUE].append(
                    {
                        "d": last_hour.replace(
                            hour=idx + 1, minute=0, second=0, microsecond=0
                        ),
                        VALUE: round((recording["y"] / recording["c"]), 1),
                    }
                )

    @property
    def state(self) -> str | None:
        """Retrieve state of the record sensor."""
        return self._data[self.attr_id].get(RESULT, {}).get(VALUE)

    def build_uri(self, time: datetime) -> str:
        interval = (time - timedelta(hours=1)).strftime("%Y-%m-%d")
        return f"{self._data[self.attr_id][URI]}?{INTERVAL}={interval}"

    async def update(self, time: datetime = datetime.utcnow()) -> None:
        """Update info about Recording Sensor asynchronously."""
        try:
            result = await self._connector.get(self.build_uri(time))
            self.process_results(result, time)
        except DeviceException as err:
            _LOGGER.error(
                f"Can't update data for {self.name}. Trying uri: {self._data[URI]}. Error message: {err}"
            )
            self._extra_message = f"Can't update data. Error: {err}"
