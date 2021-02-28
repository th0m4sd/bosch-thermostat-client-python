"""Circuits module of Bosch thermostat."""
import logging
from bosch_thermostat_client.const import ID, CIRCUIT_TYPES, HC, DHW, SC, REFERENCES
from bosch_thermostat_client.helper import BoschEntities
from .circuit import BasicCircuit
from .ivt_circuit import IVTCircuit
from .nefit_circuit import NefitCircuit
from bosch_thermostat_client.const.ivt import IVT

_LOGGER = logging.getLogger(__name__)


def choose_circuit_type(device_type):
    return IVTCircuit if device_type == IVT else NefitCircuit


class Circuits(BoschEntities):
    """Circuits main object containing multiple Circuit objects."""

    def __init__(self, connector, circuit_type, bus_type, device_type):
        """
        Initialize circuits.

        :param obj get -> get function
        :param obj put -> put http function
        :param str circuit_type: is it HC or DHW
        """
        self._circuit_type = (
            circuit_type if circuit_type in CIRCUIT_TYPES.keys() else None
        )
        self._connector = connector
        self._bus_type = bus_type
        self._device_type = device_type
        super().__init__(connector.get)

    @property
    def circuits(self):
        """Get circuits."""
        return self.get_items()

    async def initialize(self, database, current_date):
        """Initialize HeatingCircuits asynchronously."""
        if not self._circuit_type:
            return None
        db_prefix = CIRCUIT_TYPES[self._circuit_type]
        if db_prefix not in database:
            _LOGGER.debug("Circuit not exist in database %s", db_prefix)
            return None
        circuits = await self.retrieve_from_module(1, f"/{db_prefix}")
        for circuit in circuits:
            if REFERENCES in circuit:
                circuit_object = self.create_circuit(circuit, database, current_date)
                if circuit_object:
                    await circuit_object.initialize()
                    if circuit_object.state:
                        self._items.append(circuit_object)

    def create_circuit(self, circuit, database, current_date):
        """Create single circuit of given type."""
        if self._circuit_type in (HC, DHW):
            Circuit = choose_circuit_type(self._device_type)
            return Circuit(
                self._connector,
                circuit[ID],
                database,
                self._circuit_type,
                self._bus_type,
                current_date,
            )
        elif self._circuit_type == SC:
            return BasicCircuit(
                self._connector,
                circuit[ID],
                database,
                self._circuit_type,
                self._bus_type,
            )
        return None
