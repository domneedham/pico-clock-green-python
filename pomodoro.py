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
        scheduler.schedule(SCHEDULER_POMODORO_SECOND, 1000, self.secs_callback)
        self.pomodoro_duration = 25*60  # 25 mins

    async def enable(self):
        self.enabled = True
        t = "%02d:%02d" % (self.pomodoro_duration // 60,
                           self.pomodoro_duration % 60)
        await self.display.show_text(t)
        self.buttons.add_callback(2, self.start_callback, max=500)
        self.buttons.add_callback(2, self.clear_callback, min=500)

    def disable(self):
        self.enabled = False
        self.started = False
        self.start_time = None

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

    async def secs_callback(self):
        if self.enabled and self.started:
            now = int(self._time_left())
            t = "%02d:%02d" % (now // 60, now % 60)
            await self.display.show_text(t)
            if now <= 0:
                self.speaker.beep(1000)
                self.started = False
                self.start_time = None
                self.time_left = None

    async def start_callback(self):
        if self.enabled and self.started:
            self.stop()
        else:
            print("START POMODORO")
            self.start()

    async def clear_callback(self):
        self.stop()
        await self.enable()
