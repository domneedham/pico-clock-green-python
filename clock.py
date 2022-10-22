from apps import App
from constants import SCHEDULER_CLOCK_SECOND
from display import Display
from rtc import RTC
from buttons import Buttons
from configuration import Configuration
import helpers


class Clock(App):
    def __init__(self, scheduler):
        App.__init__(self, "Clock", "clock")
        self.config = Configuration()
        self.display = Display(scheduler)
        self.rtc = RTC()
        self.enabled = True
        self.buttons = Buttons(scheduler)
        self.hour = 0
        self.minute = 0
        self.second = 0
        scheduler.schedule(SCHEDULER_CLOCK_SECOND, 1000, self.secs_callback)

    def enable(self):
        self.enabled = True
        self.update_time(force_show_time=True)
        self.buttons.add_callback(2, self.temp_callback, max=500)
        self.buttons.add_callback(
            2, self.switch_temperature_callback, min=500, max=5000)
        self.buttons.add_callback(3, self.backlight_callback, max=500)
        self.buttons.add_callback(
            3, self.switch_blink_callback, min=500, max=5000)

    def disable(self):
        self.enabled = False

    def secs_callback(self):
        if self.enabled:
            self.update_time()
            if self.should_blink():
                if self.second % 2 == 0:
                    # makes : display
                    self.display.show_char(":", pos=10)
                else:
                    # makes : not display
                    self.display.show_char(" :", pos=10)

    def should_blink(self):
        return self.config.blink_time_colon and not self.display.animating and self.display.showing_time

    def update_time(self, force_show_time=False):
        t = self.rtc.get_time()
        self.second = t[5]
        if self.hour != t[3] or self.minute != t[4] or force_show_time:
            self.hour = t[3]
            self.minute = t[4]
            self.show_time_icon()
            self.show_time()
            self.display.show_day(t[6])
        elif t[5] == 20:
            self.show_temperature()

    def show_time(self):
        hour = self.hour
        if self.config.clock_type == "12":
            hour = helpers.convert_twenty_four_to_twelve_hour(hour)
        self.display.show_time("%02d:%02d" % (hour, self.minute))

    def show_time_icon(self):
        if self.hour >= 12:
            self.display.show_icon("PM")
            self.display.hide_icon("AM")
        else:
            self.display.show_icon("AM")
            self.display.hide_icon("PM")

    def show_temperature(self):
        temp = self.rtc.get_temperature()
        self.display.show_temperature(temp)

    def temp_callback(self):
        self.show_temperature()

    def switch_temperature_callback(self):
        self.config.switch_temp_value()
        self.display.show_temperature_icon()

    def backlight_callback(self):
        self.display.switch_backlight()

    def switch_blink_callback(self):
        self.config.switch_blink_time_colon_value()
