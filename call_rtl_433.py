import threading
import subprocess
import time
import queue
import json
import rrdtool
from pathlib import Path

import WeatherData
import RepeatedTimer

class PollRTL433(threading.Thread):
    def __init__(self, out_q):
        super(PollRTL433, self).__init__()
        self.stdout = None
        self.stderr = None
        self.out_q = out_q
        self.stoprequest = threading.Event()

    def run(self):
        p = subprocess.Popen('rtl_433 -R 16 -F json -M time'.split(),
                             shell=False,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)

        while not self.stoprequest.isSet():
            try:
                self.out_q.put((self.name, p.stdout.readline()))
            except queue.Empty:
                continue

    def join(self, timeout=None):
        self.stoprequest.set()
        super(PollRTL433, self).join(timeout)

DB_PATH = Path("db/weather.rrd")
BACKUP_PATH = Path("db/weather_dump.xml")

CREATE_ARGS = [
    "--start", "now",
    "--step", "900",
    "DS:temperature_C:GAUGE:1200:-40:50",
    "DS:humidity:GAUGE:1200:0:100",
    "DS:wind_speed:GAUGE:1200:0:30",
    "DS:wind_gust:GAUGE:1200:0:30",
    "DS:wind_direction:GAUGE:1200:0:359",
    "DS:rain_total:DDERIVE:1200:0:100",
    "RRA:AVERAGE:0.5:1:105120",
    "RRA:MIN:0.5:12:87600",
    "RRA:MAX:0.5:12:87600",
    "RRA:AVERAGE:0.5:12:87600"
]

if not DB_PATH.is_file():
    rrdtool.create(DB_PATH.as_posix(), *CREATE_ARGS)

out_q = queue.Queue(256)
rtl_433 = PollRTL433(out_q=out_q)
rtl_433.start()

while True:
    while not out_q.empty():
        test = out_q.get_nowait()
        weather_datum = WeatherData.from_json(test[1])
        if weather_datum.time is not None:
            timestamp_str = str(weather_datum.time.timestamp())
        else:
            timestamp_str = "N"
        rrdtool.update(DB_PATH.as_posix(), weather_datum.to_rrd())
    time.sleep(5)