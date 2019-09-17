import json
from time import strptime as strptime

class WeatherData:
    def __init__(self, time=None, model=None, id=None, channel=None, battery=None, mic=None):
        self.time = strptime(time, "%Y-%m-%d %H:%M:%S")
        self.model = model
        self.id = id
        self.channel = channel
        self.battery = battery
        self.mic = mic

    _model = None
    _id = None

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
        self.wind_direction = wind_direction

    _model = "AlectoV1 Wind Sensor"
    _id = 98

class RainData(WeatherData):
    def __init__(self, rain_total=None, *args, **kwargs):
        super(RainData, self).__init__(*args, **kwargs)
        self.rain_total = rain_total
    
    _model = "AlectoV1 Rain Sensor"
    _id = 206

class TemperatureData(WeatherData):
    def __init__(self, temperature_C=None, humidity=None, *args, **kwargs):
        super(TemperatureData, self).__init__(*args, **kwargs)
        self.temperature_C = temperature_C
        self.humidity = humidity

    _model = "AlectoV1 Temperature Sensor"
    _id = 98

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