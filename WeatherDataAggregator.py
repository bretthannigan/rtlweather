import statistics
import WeatherData

class WeatherDataAggregator:
    # This class was added because RRDTool does not accept asynchronous upates. 
    # Instead, must keep most recent WeatherData objects of each type until ready for the synchronous update.
    def __init__(self):
        self._TemperatureDataPoints = []
        self._WindDataPoints = []
        self._RainDataPoints = []

    def add(self, wd):
        if type(wd) is WeatherData.TemperatureData:
            self._TemperatureDataPoints.append(wd)
        elif type(wd) is WeatherData.WindData:
            self._WindDataPoints.append(wd)
        elif type(wd) is WeatherData.RainData:
            self._RainDataPoints.append(wd)

    def _merge_TemperatureDataPoints(self):
        # Average all temperature and humidity readings.
        if self._TemperatureDataPoints:
            merged = self._TemperatureDataPoints[-1]
            temperature_Cs = []
            humiditys = []
            for dp in self._TemperatureDataPoints:
                temperature_Cs.append(dp.temperature_C)
                humiditys.append(dp.humidity)
            merged.temperature_C = statistics.mean(temperature_Cs)
            merged.humiditys = statistics.mean(humiditys)
        else:
            merged = WeatherData.TemperatureData()
        return merged

    def _merge_WindDataPoints(self):
        # Average all collected wind speeds and directions, keep highest wind gust.
        if self._WindDataPoints:
            merged = self._WindDataPoints[-1]
            wind_speeds = []
            wind_gusts = []
            wind_direction = []
            for dp in self._WindDataPoints:
                wind_speeds.append(dp.wind_speed)
                wind_gusts.append(dp.wind_gust)
                wind_direction.append(dp.wind_direction)
            merged.wind_speed = statistics.mean(wind_speeds)
            merged.wind_gust = max(wind_gusts)
            merged.wind_direction = statistics.mean(wind_direction)
        else:
            merged = WeatherData.WindData
        return merged

    def _merge_RainDataPoints(self):
        # Keep last cumulative rain total.
        if self._RainDataPoints:
            merged = self._RainDataPoints[-1]
        else:
            merged = WeatherData.RainData()
        return merged

    def to_rrd():
        td_args = self._merge_TemperatureDataPoints().to_rrd()
        wd_args = self._merge_WindDataPoints().to_rrd()
        rd_args = self._merge_RainDataPoints().to_rrd()
        args = []
        args.append(td_args[0])
        args.append(":".join((td_args[1], wd_args[1], rd_args[1])))
        args.append(":".join((td_args[2], wd_args[2], rd_args[2])))
        print(args)
        return args
