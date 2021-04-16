"""
Class to control /program/list in EasyControl.
"""
from datetime import datetime, timedelta
from bosch_thermostat_client.const import NAME, ID, VALUE
from bosch_thermostat_client.helper import check_base64


class ZonePrograms:
    def __init__(self, program_uri, connector):
        self._last_updated = None
        self._program_uri = program_uri
        self._connector = connector
        self._program_list = []
        self._short_program_list = []

    async def update(self):
        now = datetime.now()
        if self._last_updated and now - self._last_updated < timedelta(minutes=10):
            return
        res = await self._connector.get(self._program_uri)
        program_list = res.get(VALUE, [])
        for item in program_list:
            name = check_base64(item[NAME])
            program_exists = self.get_preset_index_by_name(name)
            if not program_exists:
                self._program_list.append({ID: item[ID], NAME: name})
                self._short_program_list.append(name)
        self._last_updated = datetime.now()

    @property
    def preset_names(self):
        return self._short_program_list

    def preset_name(self, active_program):
        if len(self._program_list) > 0:
            for program in self._program_list:
                if active_program == program[ID]:
                    return program[NAME]

    def get_preset_index_by_name(self, name):
        if len(self._program_list) > 0:
            for program in self._program_list:
                if name == program[NAME]:
                    return program[ID]
