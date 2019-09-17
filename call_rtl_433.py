import threading
import subprocess
import time
import queue
import json
import rrdtool
from pathlib import Path

import WeatherData

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

DB_PATH = Path("/db/weather.rrd")
BACKUP_PATH = Path("/db/weather_dump.xml")

if not my_file.is_file():
    rrdtool.create(
        DB_PATH.as_posix(),
        "--start", "now",
        "--step", "900",
        "DS:temperature:GAUGE:1200:-40:50",
        "DS:humidity:GAUGE:1200:0:100",
        "DS:wind_speed:GAUGE:1200:0:30",
        "DS:wind_gust:GAUGE:1200:0:30",
        "DS:wind_direction:GAUGE:1200:0:359",
        "DS:rainfall:DERIVE:1200:0:100",
        "RRA:AVERAGE:0.5:1:105120",
        "RRA:MIN:0.5:12:87600",
        "RRA:MAX:0.5:12:87600",
        "RRA:AVERAGE:0.5:12:87600"
    )
else:
    rrdtool.create(
        DB_PATH.as_posix(),
        "--step", "900",
        "--source", DB_PATH.as_posix(),
        
    )

out_q = queue.Queue(256)
rtl_433 = PollRTL433(out_q=out_q)
rtl_433.start()

while out_q.empty():
    pass

#json_data = out_q.get_nowait()
#test = WeatherData.from_json(json_data[1])

while True:
    while not out_q.empty():
        test = out_q.get_nowait()
        weather_datum = WeatherData.from_json(test[1])
        if isinstance(weather_datum, WeatherData.WindData):

        elif isinstance(weather_datum, WeatherData.RainData):

        elif isinstance(weather_datum, WeatherData.TemperatureData):

    time.sleep(5)