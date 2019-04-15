import json

class WeatherData:
    def __init__(self, time=None, model=None, id=None, channel=None, battery=None, mic=None):
        self.time = time
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

    @classmethod
    def is_model(cls, mdl):
        return mdl == "AlectoV1 Wind Sensor"

class RainData(WeatherData):
    def __init__(self, rain_total=None, *args, **kwargs):
        super(RainData, self).__init__(*args, **kwargs)
        self.rain_total = rain_total
    
    @classmethod
    def is_model(cls, mdl):
        return mdl == "AlectoV1 Rain Sensor"

class TemperatureData(WeatherData):
    def __init__(self, temperature_C=None, humidity=None, *args, **kwargs):
        super(TemperatureData, self).__init__(*args, **kwargs)
        self.temperature_C = temperature_C
        self.humidity = humidity

    @classmethod
    def is_model(cls, mdl):
        return mdl == "AlectoV1 Temperature Sensor"

def from_json(json_str):
    json_dict = json.loads(json_str)
    for cls in WeatherData.__subclasses__():
        if cls.is_model(json_dict['model']):
            return cls(**json_dict)