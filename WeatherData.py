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

class WindData(WeatherData):
    def __init__(self, wind_speed=None, wind_gust=None, wind_direction=None, *args, **kwargs):
        super(WindData, self).__init__(*args, **kwargs)
        self.wind_speed = wind_speed
        self.wind_gust = wind_gust
        self.wind_direction = wind_direction

    _model = "AlectoV1 Wind Sensor"

    @classmethod
    def is_model(cls, mdl):
        return mdl == cls._model

class RainData(WeatherData):
    def __init__(self, rain_total=None, *args, **kwargs):
        super(RainData, self).__init__(*args, **kwargs)
        self.rain_total = rain_total
    
    _model = "AlectoV1 Rain Sensor"

    @classmethod
    def is_model(cls, mdl):
        return mdl == cls._model

class TemperatureData(WeatherData):
    def __init__(self, temperature_C=None, humidity=None, *args, **kwargs):
        super(TemperatureData, self).__init__(*args, **kwargs)
        self.temperature_C = temperature_C
        self.humidity = humidity

    _model = "AlectoV1 Temperature Sensor"

    @classmethod
    def is_model(cls, mdl):
        return mdl == cls._model

def from_json(json_str):
    """
    Instantiates a subclass of WeatherData based on the 'model' field of the JSON input string.
    """
    json_dict = json.loads(json_str)
    for cls in WeatherData.__subclasses__():
        if cls.is_model(json_dict['model']):
            return cls(**json_dict)