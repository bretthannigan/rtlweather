import json
from datetime import datetime
from tzlocal import get_localzone
import statistics

class WeatherData:
    def __init__(self, time=None, model=None, id=None, channel=None, battery=None, mic=None):
        if time is not None:
            self.time = datetime.strptime(time, "%Y-%m-%d %H:%M:%S").astimezone(get_localzone())
        else:
            self.time = None
        self.model = model
        self.id = id
        self.channel = channel
        self.battery = battery
        self.mic = mic

    _model = None
    _id = None

    def to_rrd(self, names):
        rrd_args = ["--template"]
        rrd_args.append(":".join(names))
        if self.time is not None:
            rrd_val = str(self.time.timestamp())
        else:
            rrd_val = "N"
        for name in names:
            rrd_val = rrd_val + ":" + str(getattr(self, name))
        rrd_args.append(rrd_val)
        return rrd_args

    def __str__(self):
        return '{:<25}'.format(str(self.time))

    @classmethod
    def is_model(cls, mdl):
        return mdl == cls._model

    @classmethod
    def is_id(cls, id):
        return id == cls._id

class WindData(WeatherData):
    def __init__(self, wind_speed="U", wind_gust="U", wind_direction="U", *args, **kwargs):
        super(WindData, self).__init__(*args, **kwargs)
        self.wind_speed = wind_speed
        self.wind_gust = wind_gust
        self.wind_direction = wind_direction

    _model = "AlectoV1 Wind Sensor"
    _id = 98

    def to_rrd(self):
        property_names = ["wind_speed", "wind_gust", "wind_direction"]
        return super(WindData, self).to_rrd(property_names)

    def __str__(self):
        line = super(WindData, self).__str__()
        line = line + '\t' + type(self).__name__ + '\n' + \
            '\tWind speed: {:2.2f} m/s {:<3}\n'.format(self.wind_speed, self.degrees_to_compass_heading()) + \
            '\tGust speed: {:2.2f} m/s\n'.format(self.wind_gust)
        return line

    def degrees_to_compass_heading(self):
        directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
        return directions[(int((self.wind_direction/22.5)+0.5) % 16)]

class RainData(WeatherData):
    def __init__(self, rain_total="U", *args, **kwargs):
        super(RainData, self).__init__(*args, **kwargs)
        self.rain_total = rain_total
    
    _model = "AlectoV1 Rain Sensor"
    _id = 200

    def to_rrd(self):
        property_names = ["rain_total"]
        return super(RainData, self).to_rrd(property_names)

    def __str__(self):
        line = super(RainData, self).__str__()
        line = line + '\t' + type(self).__name__ + '\n' + \
            '\tCumulative rainfall: {:4.2f} mm\n'.format(self.rain_total)
        return line

class TemperatureData(WeatherData):
    def __init__(self, temperature_C="U", humidity="U", *args, **kwargs):
        super(TemperatureData, self).__init__(*args, **kwargs)
        self.temperature_C = temperature_C
        self.humidity = humidity

    _model = "AlectoV1 Temperature Sensor"
    _id = 98

    def to_rrd(self):
        property_names = ["temperature_C", "humidity"]
        return super(TemperatureData, self).to_rrd(property_names)

    def __str__(self):
        line = super(TemperatureData, self).__str__()
        line = line + '\t' + type(self).__name__ + '\n' + \
            '\tTemperature: {:2.1f} C\n'.format(self.temperature_C) + \
            '\tHumidity: {:2.0f}%\n'.format(self.humidity)
        return line

def from_json(json_str):
    """
    Instantiates a subclass of WeatherData based on the 'model' field of the JSON input string.
    """
    try:
        json_dict = json.loads(json_str)
    except json.decoder.JSONDecodeError:
        return None
    if 'model' in json_dict and 'id' in json_dict:
        # ID seems to change every time batteries are replaced. For now, ignore.
        for cls in WeatherData.__subclasses__():
            if cls.is_model(json_dict['model']): #and cls.is_id(json_dict['id']):
                return cls(**json_dict)
    else:
        return None

class WeatherDataAggregator:
    # This class was added because RRDTool does not accept asynchronous upates. 
    # Instead, must keep most recent WeatherData objects of each type until ready for the synchronous update.
    def __init__(self):
        self.reset()

    def reset(self):
        self._TemperatureDataPoints = []
        self._WindDataPoints = []
        self._RainDataPoints = []

    def add(self, wd):
        if type(wd) is TemperatureData:
            self._TemperatureDataPoints.append(wd)
        elif type(wd) is WindData:
            self._WindDataPoints.append(wd)
        elif type(wd) is RainData:
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
            merged = TemperatureData()
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
            merged = WindData()
        return merged

    def _merge_RainDataPoints(self):
        # Keep last cumulative rain total.
        if self._RainDataPoints:
            merged = self._RainDataPoints[-1]
        else:
            merged = RainData()
        return merged

    def to_rrd(self):
        td = self._merge_TemperatureDataPoints()
        td_args = td.to_rrd()
        wd = self._merge_WindDataPoints()
        wd_args = wd.to_rrd()
        rd = self._merge_RainDataPoints()
        rd_args = rd.to_rrd()
        args = []
        args.append(td_args[0])
        args.append(":".join((td_args[1], wd_args[1], rd_args[1])))
        # The following 6 lines strip the date from the RRDTool string.
        i_date_end = td_args[2].find(":")
        td_args[2] = td_args[2][(i_date_end+1):]
        i_date_end = wd_args[2].find(":")
        wd_args[2] = wd_args[2][(i_date_end+1):]
        i_date_end = rd_args[2].find(":")
        rd_args[2] = rd_args[2][(i_date_end+1):]
        args.append(":".join(("N", td_args[2], wd_args[2], rd_args[2])))
        return args