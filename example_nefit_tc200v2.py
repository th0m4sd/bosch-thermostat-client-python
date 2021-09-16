""" Test script of bosch_thermostat_client. """
import asyncio
from bosch_thermostat_client.const.easycontrol import EASYCONTROL
import logging
import time
import bosch_thermostat_client as bosch
from bosch_thermostat_client.const import XMPP

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger("aioxmpp").setLevel(logging.WARN)
logging.getLogger("aioopenssl").setLevel(logging.WARN)
logging.getLogger("aiosasl").setLevel(logging.WARN)
logging.getLogger("asyncio").setLevel(logging.WARN)


async def main():
    """
    Provide data_file.txt with ip, access_key, password and check
    if you can retrieve data from your thermostat.
    """
    data_file = open("data_file_easycontrol.txt", "r")
    data = data_file.read().splitlines()
    BoschGateway = bosch.gateway_chooser(device_type=EASYCONTROL)
    gateway = BoschGateway(
        session=asyncio.get_event_loop(),
        session_type=XMPP,
        host=data[0],
        access_token=data[1],
        password=data[2],
    )
    await gateway.initialize()
    print(f"UUID {await gateway.check_connection()}")
    return

    # small = await gateway.smallscan(DHW_CIRCUITS)
    #        myjson = json.loads(small)
    # print(small)
    # return
    sensors = await gateway.initialize_sensors()
    for sensor in sensors:
        await sensor.update()
    for sensor in sensors:
        print(f"{sensor.name} : {sensor.state}")
    await gateway.get_capabilities()
    # for hc in gateway.dhw_circtuis:
    #     await hc.update()
    #     print("hvac mode", hc.ha_mode)
    #     print("target temp ->", hc.target_temperature)
    return

    #        await hc.set_ha_mode("auto") #MEANS AUTO
    #       await hc.update()
    # time.sleep(4)
    await dhw.set_temperature(53.0)
    # return
    # return
    # await dhw.set_ha_mode("performance") #MEANS MANUAL
    return
    # print("target in manual", hc.target_temperature)
    # print("ha mode in manual", hc.ha_mode)
    # await hc.update()
    # print("target after update", hc.target_temperature)
    # print("ha mode", hc.ha_mode)

    # await hc.set_ha_mode("auto") #MEANS AUTO
    # print("target after auto without update", hc.target_temperature)
    # print("ha mode", hc.ha_mode)

    # return
    # print(await hc.set_temperature(10.0))
    # print("ustawiona!")
    dhws = gateway.dhw_circuits
    dhw = dhws[0]
    await dhw.update()
    print("START1")
    print(dhw.target_temperature)
    print("START2")
    print(dhw.current_mode)
    print(dhw.target_temperature)

    return
    print("START3")
    print(dhw.target_temperature)
    return
    # print(hc.schedule)
    print(gateway.get_info(DATE))
    # print(await gateway.rawscan())
    # print(hc.schedule.get_temp_for_date(gateway.get_info(DATE)))
    return
    aa = 0
    while aa < 10:
        time.sleep(1)
        await hc.update()
        print(hc.target_temperature)
        aa = aa + 1

    await hc.set_operation_mode("auto")

    aa = 0
    while aa < 10:
        time.sleep(1)
        await hc.update()
        print(hc.target_temperature)
        aa = aa + 1

    # print(gateway.get_property(TYPE_INFO, UUID))
    await loop.close()


asyncio.run(main())

# asyncio.get_event_loop().run_until_complete(main())
