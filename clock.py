from apps import App
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
        self.showing_temperature = False
        scheduler.schedule("clock-second", 1000, self.secs_callback)

    def enable(self):
        self.enabled = True
        self.update_time()
        self.buttons.add_callback(3, self.backlight_callback, max=500)

    def disable(self):
        self.enabled = False

    def secs_callback(self, t):
        if self.enabled:
            self.update_time()
            if self.config.blink_time_colon and not self.showing_temperature:
                if self.second % 2 == 0:
                    # makes : display
                    self.display.show_char(":", pos=10)
                else:
                    # makes : not display
                    self.display.show_char(" :", pos=10)

    def update_time(self):
        t = self.rtc.get_time()
        self.second = t[5]
        if self.hour != t[3] or self.minute != t[4]:
            self.showing_temperature = False
            self.hour = t[3]
            self.minute = t[4]
            self.show_time_icon()
            self.show_time()
            self.display.show_day(t[6])
        elif t[5] == 20:
            self.showing_temperature = True
            temp = self.rtc.get_temperature()
            self.display.show_temperature(temp)
        elif t[5] == 23:
            self.display.show_text("HE")
        elif t[5] == 25:
            self.display.animate_text("H1")

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

    def backlight_callback(self, t):
        self.display.switch_backlight()
