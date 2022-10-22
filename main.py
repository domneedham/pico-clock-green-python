from utime import sleep
from pico_temperature import PicoTemperature
from scheduler import Scheduler
from clock import Clock
from apps import Apps, App
from pomodoro import Pomodoro
from temperature import Temperature
from time_set import TimeSet
from wifi import WLAN
from mqtt import MQTT
from configuration import Configuration
import machine
import uasyncio


machine.freq(250_000_000)

APP_CLASSES = [
    Clock,
    Pomodoro,
    TimeSet
]

print("-" * 10)
print("PICO CLOCK")
print("-" * 10)

print("Configuring...")
config = Configuration()

scheduler = Scheduler()
wlan = WLAN(scheduler)
mqtt = MQTT(scheduler)
pico_temperature = PicoTemperature(scheduler, mqtt)
temperature = Temperature(mqtt)
apps = Apps(scheduler)
for App in APP_CLASSES:
    apps.add(App(scheduler))

print("STARTING...")
scheduler.start()

loop = uasyncio.get_event_loop()
loop.run_forever()
