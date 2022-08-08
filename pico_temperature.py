import machine
from mqtt import MQTT
from scheduler import Scheduler
from util import singleton


@singleton
class PicoTemperature:
    def __init__(self, scheduler: Scheduler, mqtt: MQTT):
        self.scheduler = scheduler
        self.mqtt = mqtt
        self.sensor = machine.ADC(4)
        self.conversion_factor = 3.3 / (65535)
        self.temperature = 0
        mqtt.register_state_callback(
            "device_temperature", self.mqtt_state_callback)

    def get_temperature(self):
        reading = self.sensor.read_u16() * self.conversion_factor
        self.temperature = 27 - (reading - 0.706)/0.001721
        return self.temperature

    def mqtt_state_callback(self):
        temp = self.get_temperature()
        return str(temp)
