from machine import Timer
import time
import _thread


class Scheduler:
    class Schedule:
        def __init__(self, name, duration, callback, initial_delay):
            self.name = name
            self.duration = duration
            self.callback = callback
            self.initial_delay = initial_delay
            self.wait_for_delay = False
            if self.initial_delay != 0:
                self.wait_for_delay = True
            self.lastrun = time.ticks_ms()

    def __init__(self):
        self.schedules = []
        self.display_schedules = []
        self.lock = _thread.allocate_lock()

    def start(self):
        self._start_timer()
        self._start_display_timer()

    def _start_timer(self):
        tim = Timer()
        tim.init(period=1, mode=Timer.PERIODIC,
                 callback=self.event_callback)

    def _start_display_timer(self):
        tim = Timer()
        tim.init(period=1, mode=Timer.PERIODIC,
                 callback=self.display_event_callback)

    def schedule(self, name, duration, callback, initial_delay=0):
        self.schedules.append(self.Schedule(
            name, duration, callback, initial_delay))

    def schedule_display(self, name, duration, callback, initial_delay=0):
        self.display_schedules.append(self.Schedule(
            name, duration, callback, initial_delay))

    def remove(self, name):
        for schedule in self.schedules:
            if schedule.name == name:
                self.schedules.remove(schedule)

    def remove_display_schedule(self, name):
        for schedule in self.display_schedules:
            if schedule.name == name:
                self.display_schedules.remove(schedule)

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
