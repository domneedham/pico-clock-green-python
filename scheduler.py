from constants import SCHEDULER_ENABLE_LEDS
import uasyncio
import _thread


class Scheduler:
    class Schedule:
        def __init__(self, name: str, duration: int, callback: uasyncio.Task, initial_delay: int):
            self.name = name
            self.duration = duration
            self.callback = callback
            self.initial_delay = initial_delay
            self.cancelled = False

    def __init__(self):
        self.started = False
        self.schedules = []
        self.display_task = None
        self.event_loop = uasyncio.get_event_loop()

    def start(self):
        self.started = True
        for schedule in self.schedules:
            self.event_loop.create_task(self._start_task(schedule))

        _thread.start_new_thread(self._start_display, ())

    def _start_display(self):
        self._start_display_task(self.display_task)

    def _start_display_task(self, task: Schedule):
        while True:
            task.callback()

    async def _start_task(self, task: Schedule):
        if task.initial_delay != 0:
            await uasyncio.sleep_ms(task.initial_delay)
        while True:
            if task.cancelled:
                break
            await task.callback()
            await uasyncio.sleep_ms(task.duration)

    def schedule(self, name, duration, callback, initial_delay=0):
        task = self.Schedule(name, duration, callback, initial_delay)
        if task.name == SCHEDULER_ENABLE_LEDS:
            self.display_task = task
        else:
            self.schedules.append(task)
            if self.started:
                self.event_loop.create_task(self._start_task(task))

    def remove(self, name):
        for schedule in self.schedules:
            if schedule.name == name:
                schedule.cancelled = True
                self.schedules.remove(schedule)
