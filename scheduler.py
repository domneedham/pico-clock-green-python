import uasyncio


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
        self.event_loop = uasyncio.get_event_loop()

    def start(self):
        self.started = True
        for schedule in self.schedules:
            self.event_loop.create_task(self._start_task(schedule))

    async def _start_task(self, task: Schedule):
        if task.initial_delay != 0:
            await uasyncio.sleep_ms(task.initial_delay)
        while True:
            if task.cancelled:
                break
            task.callback()
            await uasyncio.sleep_ms(task.duration)

    def schedule(self, name, duration, callback, initial_delay=0):
        task = self.Schedule(name, duration, callback, initial_delay)
        self.schedules.append(task)

        if self.started:
            self.event_loop.create_task(self._start_task(task))

    def remove(self, name):
        for schedule in self.schedules:
            if schedule.name == name:
                schedule.cancelled = True
                self.schedules.remove(schedule)
