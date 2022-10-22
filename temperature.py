from machine import SoftI2C
from machine import Pin
from ds3231_port import DS3231
from util import singleton
from mqtt import MQTT


@singleton
class Temperature:
    def __init__(self, mqtt: MQTT):
        self.mqtt = mqtt
        rtc_i2c = SoftI2C(scl=Pin(7), sda=Pin(6), freq=100000)  # type: ignore
        self.ds = DS3231(rtc_i2c)
        mqtt.register_state_callback("temperature", self.get_temperature)
        pass

    def get_time(self):
        return self.ds.get_time()

    def save_time(self, t):
        return self.ds.save_time(t)

    def get_temperature(self):
        return self.ds.get_temperature()
