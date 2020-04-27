

# bosch-thermostat-client-python
Python3 asyncio package to talk to Bosch Thermostats via their gateway.
Suppored protocols are HTTP and XMPP.

Both are still in development.

example :
Follow examples dir and try to figure it out or post issue/contact on discord on more instructions.

To run this code do the following:

* create file data_file.txt and insert like this:
```
ip
access_key
password
```
replace strings with proper values

* run in dir `python3 -m venv .`
* run `python3 test.py`

# Helper
Now there is extra command added with this package `bosch_scan`.
```
Usage: bosch_scan [OPTIONS] COMMAND [ARGS]...

  A tool to create rawscan of Bosch thermostat.

Options:
  --ip TEXT                       IP address of gateway  [required]
  --token TEXT                    Token from sticker without dashes.
                                  [required]
  --password TEXT                 Password you set in mobile app.
  -o, --output TEXT               Path to output file of scan. Default to
                                  [raw/small]scan_uuid.json
  --stdout                        Print scan to stdout
  -d, --debug
  -s, --smallscan [HC|DHW|SENSORS]
                                  Scan only single circuit of thermostat.
  --help                          Show this message and exit.

```

# Examples 

SENSORS:
```
bosch_examples sensors --help
bosch_examples sensors --ip {IP} --token {TOKEN} --password {PASS} -s outdoor_t1
```

DHW:
```
bosch_examples dhw --help
bosch_examples dhw --ip {IP} --token {TOKEN} --password {PASS} -t --op_modes --setpoints -m
```

HC:
```
bosch_examples hc --help
bosch_examples hc --ip {IP} --token {TOKEN} --password {PASS} -t --op_modes --setpoints -m
```