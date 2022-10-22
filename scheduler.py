from machine import Timer
import time
import uasyncio


class Scheduler:
    class Schedule:
        def __init__(self, name: str, duration: int, callback: uasyncio.Task, initial_delay: int):
            self.name = name
            self.duration = duration
            self.callback = callback
            self.initial_delay = initial_delay
            self.wait_for_delay = False
            if self.initial_delay != 0:
                self.wait_for_delay = True
            self.cancelled = False

    def __init__(self):
        self.started = False
        self.schedules = []
        self.display_schedules = []
        self.event_loop = uasyncio.get_event_loop()

    def start(self):
        self.started = True
        for schedule in self.schedules:
            self.event_loop.create_task(self._start_task(schedule))

    async def _start_task(self, task: Schedule):
        if task.wait_for_delay:
            await uasyncio.sleep_ms(task.initial_delay)
        while True:
            if task.cancelled:
                break
            task.callback()
            await uasyncio.sleep_ms(task.duration)

    # def _start_timer(self):
    #     tim = Timer()
    #     tim.init(period=1, mode=Timer.PERIODIC,
    #              callback=self.event_callback)

    # def _start_display_timer(self):
    #     tim = Timer()
    #     tim.init(period=1, mode=Timer.PERIODIC,
    #              callback=self.display_event_callback)

    def schedule(self, name, duration, callback, initial_delay=0):
        task = self.Schedule(name, duration, callback, initial_delay)
        self.schedules.append(task)

        if self.started:
            self.event_loop.create_task(self._start_task(task))

    def schedule_display(self, name, duration, callback, initial_delay=0):
        self.schedule(name, duration, callback, initial_delay)

    def remove(self, name):
        for schedule in self.schedules:
            if schedule.name == name:
                schedule.cancelled = True
                self.schedules.remove(schedule)

    def remove_display_schedule(self, name):
        self.remove(name)

    def event_callback(self, t):
        for schedule in self.schedules:
            tm = time.ticks_ms()
            if schedule.wait_for_delay:
                if time.ticks_diff(tm, schedule.lastrun) > schedule.initial_delay:
                    schedule.wait_for_delay = False
            elif schedule.duration == 1:
                schedule.callback(t)
            else:
                if time.ticks_diff(tm, schedule.lastrun) > schedule.duration:
                    schedule.callback(t)
                    schedule.lastrun = tm

    def display_event_callback(self, t):
        for schedule in self.display_schedules:
            tm = time.ticks_ms()
            if schedule.wait_for_delay:
                if time.ticks_diff(tm, schedule.lastrun) > schedule.initial_delay:
                    schedule.wait_for_delay = False
            elif schedule.duration == 1:
                schedule.callback(t)
            else:
                if time.ticks_diff(tm, schedule.lastrun) > schedule.duration:
                    schedule.callback(t)
                    schedule.lastrun = tm
