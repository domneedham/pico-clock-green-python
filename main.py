from utime import sleep
from display import Display
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
import _thread


machine.freq(250_000_000)  # type: ignore

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
display = Display(scheduler)
pico_temperature = PicoTemperature(scheduler, mqtt)
temperature = Temperature(mqtt)
apps = Apps(scheduler)

# register apps
for App in APP_CLASSES:
    apps.add(App(scheduler))


async def start():
    print("STARTING...")

    # start async scheduler
    scheduler.start()

    # create thread for UI updates.
    _thread.start_new_thread(display.enable_leds, ())

    # start apps
    await apps.start()

uasyncio.run(start())
loop = uasyncio.get_event_loop()
loop.run_forever()
