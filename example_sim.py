""" Test script of bosch_thermostat_client. """
import asyncio
import logging
import json
import aiohttp
import time
import bosch_thermostat_client as bosch
from bosch_thermostat_client.const.ivt import IVT, HTTP

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)


async def main():
    """
    Provide data_file.txt with ip, access_key, password and check
    if you can retrieve data from your thermostat.
    """
    
    async with aiohttp.ClientSession() as session:
        data_file = open("data_file_sim.txt", "r")
        # data_file = open("data_file.txt", "r")
        data = data_file.read().splitlines()
        BoschGateway = bosch.gateway_chooser(device_type=IVT)
        gateway = BoschGateway(session=session,
                               session_type=HTTP,
                               host=data[0],
                               access_token=data[1],
                               password=data[2])
        print(await gateway.check_connection())
        await gateway.get_capabilities()
        # await gateway.test_connection()
        # return
        # small = await gateway.smallscan(DHW_CIRCUITS)
#        myjson = json.loads(small)
        # print(small)
        # return
        sensors = list(gateway.sensors)
        notification_sensor = sensors[-1]
        await notification_sensor.update()
        print("=================")
        print(notification_sensor.get_data)
        print(notification_sensor.get_property("notifications"))
        # return
        # for sensor in sensors:
        #     await sensor.update()

        dhws = gateway.dhw_circuits
        print("DHWS", dhws)
        # return
        dhw = dhws[0]
        time.sleep(1)
        await dhw.update()
        print("LOW", dhw.min_temp)
        print("MAX", dhw.max_temp)
        # for sensor in dhw.sensors:
        #     await sensor.update()
        #     print(sensor.state)
        # print(dhw.sensors)
        # return
#        await hc.set_ha_mode("auto") #MEANS AUTO
 #       await hc.update()
        # time.sleep(4)
        print("hvac mode", dhw.ha_mode)
        print("current temp -->", dhw.current_temp)
        print("target temp ->", dhw.target_temperature)
        # await dhw.set_temperature(53.0)
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
        #print(hc.schedule.get_temp_for_date(gateway.get_info(DATE)))
        return
        aa=0
        while aa < 10:
            time.sleep(1)
            await hc.update()
            print(hc.target_temperature)
            aa = aa+1
        
        await hc.set_operation_mode("auto")

        aa=0
        while aa < 10:
            time.sleep(1)
            await hc.update()
            print(hc.target_temperature)
            aa = aa+1

        # print(gateway.get_property(TYPE_INFO, UUID))
        await session.close()

asyncio.get_event_loop().run_until_complete(main())
