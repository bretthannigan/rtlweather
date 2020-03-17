import json
from datetime import datetime
from tzlocal import get_localzone

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
    def __init__(self, wind_speed=None, wind_gust=None, wind_direction=None, *args, **kwargs):
        super(WindData, self).__init__(*args, **kwargs)
        self.wind_speed = wind_speed
        self.wind_gust = wind_gust
        self.wind_direction = wind_direction - self.calibration_offset

    _model = "AlectoV1 Wind Sensor"
    _id = 98
    calibration_offset = 0

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
    def __init__(self, rain_total=None, *args, **kwargs):
        super(RainData, self).__init__(*args, **kwargs)
        self.rain_total = rain_total
    
    _model = "AlectoV1 Rain Sensor"
    _id = 206

    def to_rrd(self):
        property_names = ["rain_total"]
        return super(RainData, self).to_rrd(property_names)

    def __str__(self):
        line = super(RainData, self).__str__()
        line = line + '\t' + type(self).__name__ + '\n' + \
            '\tCumulative rainfall: {:4.2f} mm\n'.format(self.rain_total)
        return line

class TemperatureData(WeatherData):
    def __init__(self, temperature_C=None, humidity=None, *args, **kwargs):
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
        for cls in WeatherData.__subclasses__():
            if cls.is_model(json_dict['model']) and cls.is_id(json_dict['id']):
                return cls(**json_dict)
    else:
        return None