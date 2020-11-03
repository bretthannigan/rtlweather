import time
import queue
import rrdtool
import signal
import sys
import os
from pathlib import Path

import WeatherData
import RepeatedTimer
import PollRTL433

class RTLWeather:

    DB_PATH = Path("db/weather.rrd")
    BACKUP_PATH = Path("db/weather_dump.xml")

    CREATE_ARGS = [
        "--start", "now",
        "--step", "300",
        "DS:temperature_C:GAUGE:1200:-40:50",
        "DS:humidity:GAUGE:1200:0:100",
        "DS:wind_speed:GAUGE:1200:0:50",
        "DS:wind_gust:GAUGE:1200:0:50",
        "DS:wind_direction:GAUGE:1200:0:359",
        "DS:rain_total:DDERIVE:1200:0:16384",
        "RRA:AVERAGE:0.5:1:105120",
        "RRA:MIN:0.5:12:87600",
        "RRA:MAX:0.5:12:87600",
        "RRA:AVERAGE:0.5:12:87600"
    ]

    DATA_UPDATE_PERIOD = 300 # s.

    def __init__(self):
        sys.stdout.write('Starting RTLWeather...\n'); sys.stdout.flush()
        if not self.DB_PATH.is_file():
            sys.stdout.write('\tCreating new database: ' + self.DB_PATH.name + '\n'); sys.stdout.flush()
            rrdtool.create(self.DB_PATH.as_posix(), *self.CREATE_ARGS)
        else:
            sys.stdout.write('\tFound existing database: ' + self.DB_PATH.name + '\n'); sys.stdout.flush()
        self.latest_data = WeatherData.WeatherDataAggregator()

    def start(self):
        sys.stdout.write('\tStarting SDR... ')
        self.out_q = queue.Queue(-1)
        self.rtl_433 = PollRTL433.PollRTL433(self.out_q)
        self.rtl_433.start()
        sys.stdout.write('Done.\n'); sys.stdout.flush()
        self.check_update_timer = RepeatedTimer.RepeatedTimer(self.DATA_UPDATE_PERIOD, self.data_update)
        sys.stdout.write('RTLWeather now scanning for packets.\n'); sys.stdout.flush()

    def data_update(self):
        print(self.out_q.qsize())
        while not self.out_q.empty():
            next_packet = self.out_q.get_nowait()
            weather_datum = WeatherData.from_json(next_packet[1])
            if weather_datum is not None:
                self.latest_data.add(weather_datum)
                sys.stdout.write(str(weather_datum)); sys.stdout.flush()
            self.out_q.task_done()
        print(self.latest_data.to_rrd())
        rrdtool.update(self.DB_PATH.as_posix(), self.latest_data.to_rrd())
        self.latest_data.reset()

    def cleanup(self):
        sys.stdout.write('Shutting down RTLWeather... '); sys.stdout.flush()
        self.rtl_433.join() # Stop RTL thread.
        self.check_update_timer.stop() # Stop periodically updating data.
        self.data_update() # Process any packets remaining in queue.
        self.out_q.join() # Block queueing of packets.
        sys.stdout.write('Done.\n'); sys.stdout.flush()
        os._exit(0)

rtlw = RTLWeather()

def cleanup_handler(signum, frame):
    # restore the original signal handler as otherwise evil things will happen
    # in raw_input when CTRL+C is pressed, and our signal handler is not re-entrant
    signal.signal(signal.SIGINT, original_sigint)
    rtlw.cleanup()
    # restore the exit gracefully handler here    
    signal.signal(signal.SIGINT, cleanup_handler)

if __name__ == '__main__':
    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, cleanup_handler)
    rtlw.start()