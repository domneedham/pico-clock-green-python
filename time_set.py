from apps import App
from buttons import Buttons
from constants import APP_TIME_SET, SCHEDULER_TIME_SET_HALF_SECOND, SCHEDULER_TIME_SET_MINUTE
from display import Display
from rtc import RTC
import uasyncio

month_max = {
    1: 31,  # January
    2: 29,  # February
    3: 31,  # March
    4: 30,  # April
    5: 31,  # May
    6: 30,  # June
    7: 31,  # July
    8: 31,  # August
    9: 30,  # September
    10: 31,  # October
    11: 30,  # November
    12: 31,  # December
}


class TimeSet(App):
    class State:
        def __init__(self, name, position, panel, index, max, length=2, offset=0):
            self.name = name
            self.position = position
            self.panel = panel
            self.index = index
            self.max = max
            self.length = length
            self.offset = offset

    def __init__(self, scheduler):
        App.__init__(self, APP_TIME_SET)

        self.display = Display(scheduler)
        self.scheduler = scheduler
        self.buttons = Buttons(scheduler)
        self.rtc = RTC()
        self.grab_top_button = True
        self.enabled = False
        self.active = False
        self.state = None
        self.state_index = -1
        self.flash_count = 0
        self.flash_state = False
        scheduler.schedule(SCHEDULER_TIME_SET_HALF_SECOND, 500,
                           self.half_secs_callback)
        scheduler.schedule(SCHEDULER_TIME_SET_MINUTE,
                           60000, self.mins_callback)
        self.initialise_states()

    def initialise_states(self):
        self.states = [
            TimeSet.State("dow", 0, "dow", 6, 7, length=7, offset=0),
            TimeSet.State("hours", 0, "time", 3, 24),
            TimeSet.State("minutes", 13, "time", 4, 60),
            TimeSet.State("year", 0, "year", 0, 3000, length=4),
            TimeSet.State("month", 0, "date", 1, 12, offset=1),
            TimeSet.State("day", 13, "date", 2, -1, offset=1),
        ]

    async def enable(self):
        self.active = True
        self.enabled = True
        self.state_index = 0
        self.state = self.states[self.state_index]
        self.display.hide_temperature_icons()
        await self.update_display()
        self.buttons.add_callback(2, self.up_callback, max=500)
        self.buttons.add_callback(3, self.down_callback, max=500)

    def disable(self):
        self.active = False
        self.enabled = False
        self.state = None

    async def half_secs_callback(self):
        if self.enabled:
            self.flash_count = (self.flash_count+1) % 3
            if self.flash_count == 2:
                if self.state.length == 2:
                    await self.display.show_text("  ", pos=self.state.position)
                elif self.state.length == 4:
                    await self.display.show_text("    ", pos=self.state.position)
                self.flash_state = False
            else:
                if not self.flash_state:
                    self.flash_state = True
                    if self.state.length == 2:
                        await self.display.show_text(
                            "%02d" % self.time[self.state.index], pos=self.state.position)
                    elif self.state.length == 4:
                        await self.display.show_text(
                            "%04d" % self.time[self.state.index], pos=self.state.position)

    async def mins_callback(self):
        if self.enabled:
            await self.update_display()

    async def update_display(self):
        self.time = self.rtc.get_time()
        self.display.reset()
        if self.state.panel == "time":
            t = self.rtc.get_time()
            now = "%02d:%02d" % (t[3], t[4])
            await self.display.show_text(now)
        elif self.state.panel == "year":
            t = self.rtc.get_time()
            now = "%04d" % (t[0])
            await self.display.show_text(now)
        elif self.state.panel == "date":
            t = self.rtc.get_time()
            now = "%02d/%02d" % (t[1], t[2])
            await self.display.show_text(now)
        elif self.state.panel == "dow":
            print ("Entering Day-of-week panel!")
            t = self.rtc.get_time()
            now = self.display.days_of_week[t[6]].upper()
            print ("Day of week: %s" % now)
            # "" % (self.display.days_of_week[ t[6] ])
            await self.display.show_text(now)
            self.display.show_day(t[6])

    async def up_callback(self):
        t = list(self.rtc.get_time())
        max = self.state.max
        if max == -1:
            # This is "day of month", which varies
            month = t[1]
            max = month_max[month]

        t[self.state.index] = (t[self.state.index]+1 -
                               self.state.offset) % max + self.state.offset
        self.rtc.save_time(tuple(t))
        self.flash_count = 0
        await self.update_display()

    async def down_callback(self):
        t = list(self.rtc.get_time())
        max = self.state.max
        if max == -1:
            # This is "day of month", which varies
            month = t[1]
            max = month_max[month]

        t[self.state.index] = (t[self.state.index]-1 -
                               self.state.offset) % max + self.state.offset
        self.rtc.save_time(tuple(t))
        self.flash_count = 0
        await self.update_display()

    async def top_button(self):
        if self.state_index == len(self.states) - 1:
            self.disable()
            await self.display.show_text("DONE")
            await uasyncio.sleep(2)
            return True
        else:
            self.flash_count = 0
            self.state_index = (self.state_index + 1) % len(self.states)
            self.state = self.states[self.state_index]
            self.display.reset()
            await self.update_display()
            return False
