# bosch-thermostat-client-python

Python3 asyncio package to talk to Bosch Thermostats via their gateway.
Supported protocols are HTTP and XMPP.

Both are still in development.

## Helper

Now there is extra command added with this package `bosch_cli`.

```shell
# Create Python virtual environment
$ python3 -m venv bosch-thermostat-client
$ source bosch-thermostat-client/bin/activate

# Install bosch-thermostat-client
$ pip install bosch-thermostat-client

# Use bosch_cli
$ bosch_cli --help
Usage: bosch_cli [OPTIONS] COMMAND [ARGS]...

  A tool to run commands against Bosch thermostat.

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  put    Send value to Bosch thermostat.
  query  Query values of Bosch thermostat.
  scan   Create rawscan of Bosch thermostat.

$ bosch_cli scan --help
Usage: bosch_cli scan [OPTIONS]

  Create rawscan of Bosch thermostat.

Options:
  --config PATH                   Read configuration from PATH.  [default:
                                  config.yml]
  --host TEXT                     IP address of gateway or SERIAL for XMPP
                                  [required]
  --token TEXT                    Token from sticker without dashes.
                                  [required]
  --password TEXT                 Password you set in mobile app.
  --protocol [XMPP|HTTP]          Bosch protocol. Either XMPP or HTTP.
                                  [required]
  --device [NEFIT|IVT|EASYCONTROL]
                                  Bosch device type. NEFIT, IVT or
                                  EASYCONTROL.  [required]
  -d, --debug                     Set Debug mode. Single debug is debug of
                                  this lib. Second d is debug of aioxmpp as
                                  well.
  -o, --output TEXT               Path to output file of scan. Default to
                                  [raw/small]scan_uuid.json
  --stdout                        Print scan to stdout
  -d, --debug
  -i, --ignore-unknown            Ignore unknown device type. Try to scan
                                  anyway. Useful for discovering new devices.
  -s, --smallscan [HC|DHW|SENSORS|RECORDINGS]
                                  Scan only single circuit of thermostat.
  --help                          Show this message and exit.
```
