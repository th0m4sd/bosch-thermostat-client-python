import click
import logging
import aiohttp
import bosch_thermostat_client as bosch
from bosch_thermostat_client.const import XMPP
from bosch_thermostat_client.const.ivt import HTTP, IVT
from bosch_thermostat_client.const.nefit import NEFIT
import json
import asyncio
from functools import wraps

_LOGGER = logging.getLogger(__name__)


def coro(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper


@click.group(invoke_without_command=True)
@click.option("--host", envvar="BOSCH_HOST", type=str, required=True, help="IP address of gateway or SERIAL for XMPP")
@click.option("--token", envvar="BOSCH_ACCESS_TOKEN", type=str, required=True, help="Token from sticker without dashes.")
@click.option("--password", envvar="BOSCH_PASSWORD", type=str, required=False, help="Password you set in mobile app.")
@click.option("--protocol", envvar="BOSCH_PROTOCOL", type=click.Choice([XMPP, HTTP], case_sensitive=False), required=True, help="Bosch protocol. Either XMPP or HTTP.")
@click.option("--device", envvar="BOSCH_DEVICE", type=click.Choice([NEFIT, IVT], case_sensitive=False), required=True, help="Bosch device type. NEFIT or IVT.")
@click.option("-o", "--output", type=str, required=False, help="Path to output file of scan. Default to [raw/small]scan_uuid.json")
@click.option("--stdout", default=False, count=True, help="Print scan to stdout")
@click.option("-d", "--debug", default=False, count=True)
@click.option("-s", "--smallscan", type=click.Choice(['HC', 'DHW', 'SENSORS'], case_sensitive=False), help="Scan only single circuit of thermostat.")
@click.pass_context
@coro
async def cli(ctx, host: str, token: str, password: str, protocol: str, device: str, output: str, stdout: int, debug: int, smallscan: str):
    """A tool to create rawscan of Bosch thermostat."""
    if debug:
        logging.basicConfig(level=logging.DEBUG)
        _LOGGER.info("Debug mode active")
        _LOGGER.debug(f"Lib version is {bosch.version.__version__}")
    else:
        logging.basicConfig(level=logging.INFO)
    logging.getLogger('aioxmpp').setLevel(logging.WARN)
    logging.getLogger('aioopenssl').setLevel(logging.WARN)
    logging.getLogger('aiosasl').setLevel(logging.WARN)
    logging.getLogger('asyncio').setLevel(logging.WARN)
    if device.upper() == NEFIT or device.upper() == IVT:
        BoschGateway = bosch.gateway_chooser(device_type=device)
    else:
        _LOGGER.error("Wrong device type.")
        return
    if protocol.upper() == XMPP:
        gateway = BoschGateway(session=asyncio.get_event_loop(),
                               session_type=XMPP,
                               host=host,
                               access_token=token,
                               password=password)
        if await gateway.check_connection():
            await scan(gateway, smallscan, output, stdout)
    elif protocol.upper() == HTTP and device.upper() == IVT:
        async with aiohttp.ClientSession() as session:
            _LOGGER.debug("Connecting to %s with token '%s' and password '%s'", host, token, password)
            gateway = BoschGateway(session=session,
                                   session_type=HTTP,
                                   host=host,
                                   access_token=token,
                                   password=password)
            _LOGGER.debug("Trying to connect to gateway.")
            if await gateway.check_connection():
                await scan(gateway, smallscan, output, stdout)
            else:
                _LOGGER.error("Couldn't connect to gateway!")
            await session.close()


async def scan(gateway, smallscan, output, stdout):
    _LOGGER.info("Successfully connected to gateway. Found UUID: %s", gateway.uuid)
    if smallscan:
        result = await gateway.smallscan(smallscan)
        out_file = output if output else f"smallscan_{gateway.uuid}.json"
    else:
        result = await gateway.rawscan()
        out_file = output if output else f"rawscan_{gateway.uuid}.json"
    if stdout:
        print(json.dumps(result, indent=4))
    else:
        with open(out_file, "w") as logfile:
            json.dump(result, logfile, indent=4)
            _LOGGER.info("Successfully saved result to file: %s", out_file)
            _LOGGER.debug("Job done.")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(cli())
