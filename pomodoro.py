import time
from apps import App
from buttons import Buttons
from constants import APP_POMODORO, SCHEDULER_POMODORO_SECOND
from display import Display
from speaker import Speaker


class Pomodoro(App):
    def __init__(self, scheduler):
        self.scheduler = scheduler
        App.__init__(self, APP_POMODORO)
        self.display = Display(scheduler)
        self.speaker = Speaker(scheduler)
        self.buttons = Buttons(scheduler)
        self.enabled = False
        self.started = False
        self.start_time = None
        self.time_left = None
        self.grab_top_button = True
        scheduler.schedule(SCHEDULER_POMODORO_SECOND, 1000, self.secs_callback)
        self.minutes = 25
        self.pomodoro_duration = self.minutes * 60

    async def enable(self):
        self.enabled = True
        self.active = True
        self.buttons.add_callback(2, self.up_callback, max=500)
        self.buttons.add_callback(3, self.down_callback, max=500)
        self.display.hide_temperature_icons()
        self.display.show_icon("CountDown")
        await self.show_time(self.pomodoro_duration)

    def disable(self):
        self.enabled = False
        self.started = False
        self.start_time = None
        self.display.hide_icon("CountDown")

    async def top_button(self):
        if self.enabled and self.started:
            self.stop()
        else:
            print("START POMODORO")
            self.start()

    async def up_callback(self):
        if self.time_left:
            now = int(self._time_left())
            self.minutes = now // 60
            self.time_left = None
        self.minutes += 1
        await self.update_pomodoro_duration()

    async def down_callback(self):
        if self.time_left:
            now = int(self._time_left())
            self.minutes = now // 60
            self.time_left = None
        if self.minutes > 1:
            self.minutes -= 1
        await self.update_pomodoro_duration()

    async def update_pomodoro_duration(self):
        self.pomodoro_duration = self.minutes * 60
        await self.show_time(self.pomodoro_duration)

    def start(self):
        self.started = True
        self.start_time = time.ticks_ms()
        if not self.time_left:
            self.time_left = self.pomodoro_duration

    def _time_left(self):
        return self.time_left - (time.ticks_diff(time.ticks_ms(), self.start_time)/1000)

    def stop(self):
        self.started = False
        self.time_left = self._time_left()

    async def show_time(self, time):
        t = "%02d:%02d" % (time // 60, time % 60)
        await self.display.show_text(t)

    async def secs_callback(self):
        if self.enabled and self.started:
            now = int(self._time_left())
            await self.show_time(now)
            if now <= 0:
                self.speaker.beep(1000)
                self.started = False
                self.start_time = None
                self.time_left = None
