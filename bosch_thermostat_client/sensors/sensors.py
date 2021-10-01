from bosch_thermostat_client.const import (
    ID,
    NAME,
    REGULAR,
    URI,
    TYPE,
    VALUE,
    RECORDING,
    RECORDERDRES,
    DEEP,
    SENSOR_TYPE,
)
from bosch_thermostat_client.helper import (
    BoschEntities,
)

from .notification import NotificationSensor
from .sensor import Sensor
from .recording import RecordingSensor
from .crawl import CrawlSensor
from .energy import EnergySensor

NOTIFICATIONS = "notifications"
STATE = "state"
ENERGY = "energy"


class Sensors(BoschEntities):
    """Sensors object containing multiple Sensor objects."""

    def __init__(self, connector, sensors_db=None, uri_prefix=None):
        """
        Initialize sensors.

        :param dict requests: { GET: get function, SUBMIT: submit function}
        """
        self._connector = connector
        super().__init__(connector.get)
        self._items = {}
        for sensor_id, sensor in sensors_db.items():
            if sensor_id not in self._items:
                if sensor_id == NOTIFICATIONS:
                    self._items[sensor_id] = NotificationSensor(
                        connector,
                        sensor_id,
                        sensor[NAME],
                        f"{uri_prefix}/{sensor[ID]}" if uri_prefix else sensor[ID],
                    )
                elif sensor_id == ENERGY:
                    self._items[sensor_id] = EnergySensor(
                        connector=connector, attr_id=sensor_id, data=sensor
                    )
                else:
                    self._items[sensor_id] = Sensor(
                        connector=connector,
                        attr_id=sensor_id,
                        name=sensor[NAME],
                        path=f"{uri_prefix}/{sensor[ID]}" if uri_prefix else sensor[ID],
                        device_class=sensor.get("device_class"),
                        state_class=sensor.get("state_class"),
                        kind=sensor.get("type", REGULAR),
                    )

    async def initialize(self, crawl_sensors):
        """Initialize recording sensors."""
        found_recordings = []
        found_crawl = []
        for record in crawl_sensors:
            if record.get(SENSOR_TYPE, "regular") == RECORDING:
                found_recordings.extend(
                    await self.retrieve_from_module(
                        deep=record[DEEP],
                        path=record[URI],
                        exclude=record.get("exclude", "_"),
                    )
                )
            else:
                retrieved = await self.retrieve_from_module(
                    deep=record[DEEP],
                    path=record[URI],
                    exclude=record.get("exclude"),
                )
                found_crawl.append(
                    {
                        VALUE: retrieved,
                        TYPE: record.get(SENSOR_TYPE),
                        STATE: record.get(STATE),
                    }
                )

        for rec in found_recordings:
            sensor_id = f'r{rec[RECORDERDRES][ID].split("/")[-1]}'
            if sensor_id not in self._items:
                self._items[sensor_id] = RecordingSensor(
                    connector=self._connector,
                    attr_id=sensor_id,
                    name=sensor_id,
                    path=rec[ID],
                )
        for item in found_crawl:
            for sens in item[VALUE]:
                sensor_id = f'r{sens[ID].split("/")[-1]}'
                if sensor_id not in self._items:
                    self._items[sensor_id] = CrawlSensor(
                        connector=self._connector,
                        attr_id=sensor_id,
                        name=sensor_id,
                        path=sens[ID],
                        kind=item[TYPE],
                        state=item[STATE],
                    )

    def __iter__(self):
        return iter(self._items.values())

    @property
    def sensors(self):
        """Get sensor list."""
        return self.get_items().values()
