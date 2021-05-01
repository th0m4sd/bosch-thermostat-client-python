""" Test script of bosch_thermostat_client. """
import asyncio
import logging
import aiohttp
import bosch_thermostat_client as bosch
from bosch_thermostat_client.const.nefit import NEFIT
from bosch_thermostat_client.const import HTTP, HC, DHW

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)


async def hc_circuits_test(gateway):
    await gateway.initialize_circuits(HC)
    hcs = gateway.heating_circuits
    hc = hcs[0]
    await hc.update()
    print("hvac mode", hc.current_temp)
    print("target temp ->", hc.target_temperature)


async def dhw_circuits_test(gateway):
    await gateway.initialize_circuits(DHW)
    circs = gateway.dhw_circuits
    circ = circs[0]
    await circ.update()
    print("DHW mode", circ.current_temp)
    print("target temp ->", circ.target_temperature)


async def main():
    """
    Provide data_file.txt with ip, access_key, password and check
    if you can retrieve data from your thermostat.
    """
    BoschGateway = bosch.gateway_chooser(device_type=NEFIT)
    async with aiohttp.ClientSession() as session:
        gateway = BoschGateway(
            session=session,
            session_type=HTTP,
            host="127.0.0.1:8080",
            access_token="ABCdEFGHIJHKL2MN",
            password="abcdef12",
        )
        await gateway.initialize()
        await dhw_circuits_test(gateway)
    return


asyncio.run(main())
