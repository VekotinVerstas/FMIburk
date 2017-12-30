"""
> PM2.5 ; PM2.5-10 ; näytteen lämpötla ; näytteen kosteus ; kotelon lämpötila
> hiukkasarvot on kalibroimatonta signaalia eli ei kerro suoraan µg/m^3 arvoja
"""

import sys
import serial
import requests
import datetime
import json

from config import URL, USERNAME, PASSWORD

class SerialReader:

    def __init__(self, port, baudrate=115200):
        self.ser = serial.Serial()
        self.ser.port = port
        self.ser.baudrate = baudrate
        self.ser.open()
        self.ser.flushInput()

    def read_forever(self):
        while True:
            val = self.ser.readline()
            if val:
                yield val


def main(port, fname=None):
    sreader = SerialReader(port)
    if fname is None:
        f = None
    else:
        f = open(fname, 'at')
    for val in sreader.read_forever():
        ts = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        val = val.strip().decode('utf-8')
        msg = '{} {}'.format(ts, val)
        # print(msg)
        fields = val.split(';')
        if len(fields) == 5:
            # print(fields)
            dstr = 'pm2_5={},pm2_5_10={},air_temp={},air_humi={},case_temp={}'.format(*fields)
            dd = {
                'idcode': 'fmiburk_001',
                'sensor': 'fmi_pm',
                'data': dstr,
            }
            # print(dd)
            r = requests.post(URL, data=dd, auth=(USERNAME, PASSWORD))  #
            # print(r)
        if f is not None:
            f.write(msg + '\n')
            f.flush()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Run me:\n    python {} /dev/ttyACM0".format(sys.argv[0]))
        sys.exit(1)
    fname = sys.argv[2] if len(sys.argv) > 2 else None
    main(sys.argv[1], fname)
