from apps import App
from constants import APP_CLOCK, SCHEDULER_CLOCK_SECOND
from display import Display
from rtc import RTC
from buttons import Buttons
from configuration import Configuration
import helpers
import time
import ntptime
import localPTZtime


class Clock(App):
    def __init__(self, scheduler):
        App.__init__(self, APP_CLOCK)
        self.config = Configuration()
        self.wifi_config = Configuration().wifi_config
        self.display = Display(scheduler)
        self.rtc = RTC()
        self.enabled = True
        self.buttons = Buttons(scheduler)
        self.hour = 0
        self.minute = 0
        self.second = 0
        scheduler.schedule(SCHEDULER_CLOCK_SECOND, 1000, self.secs_callback)

    async def enable(self):
        self.enabled = True
        self.buttons.add_callback(2, self.temp_callback, max=500)
        self.buttons.add_callback(
            2, self.switch_temperature_callback, min=500, max=5000)
        self.buttons.add_callback(3, self.backlight_callback, max=500)
        self.buttons.add_callback(
            3, self.switch_blink_callback, min=500, max=5000)
        await self.update_time()
        await self.show_time()
        self.display.show_temperature_icon()

    def disable(self):
        self.enabled = False

    async def secs_callback(self):
        if self.enabled:
            await self.update_time()
            if self.should_blink():
                if self.second % 2 == 0:
                    # makes : display
                    self.display.show_char(":", pos=10)
                else:
                    # makes : not display
                    self.display.show_char(" :", pos=10)

    def should_blink(self):
        return self.config.blink_time_colon and not self.display.animating and self.display.showing_time

    def ntp_sync(self):
        if self.wifi_config.enabled and self.wifi_config.ntp_enabled:
            try:
                ntptime.settime()
            except:
                print("NTP time sync failed")
                return False

            local_time= localPTZtime.tztime(time.time(), self.wifi_config.ntp_ptz)
            self.rtc.save_time(local_time[:8])
            return True
        return False

    async def update_time(self):
        t = self.rtc.get_time()
        self.second = t[5]
        if self.hour != t[3] or self.minute != t[4]:
            self.hour = t[3]
            self.minute = t[4]

            if self.minute == 10 and self.second == 0:
                if self.ntp_sync(): # Sync time via NTP every hour at HH:10:00
                    print("NTP time sync successful")

            self.show_time_icon()
            self.display.show_day(t[6])
            await self.show_time()
        elif t[5] == 20 and self.config.show_temp:
            await self.show_temperature()

    async def show_time(self):
        hour = self.hour
        if self.config.clock_type == "12":
            hour = helpers.convert_twenty_four_to_twelve_hour(hour)
        await self.display.show_time("%02d:%02d" % (hour, self.minute))

    def show_time_icon(self):
        if self.config.clock_type == "12":
            if self.hour >= 12:
                self.display.show_icon("PM")
                self.display.hide_icon("AM")
            else:
                self.display.show_icon("AM")
                self.display.hide_icon("PM")

    async def show_temperature(self):
        temp = self.rtc.get_temperature()
        await self.display.show_temperature(temp)

    async def temp_callback(self):
        await self.show_temperature()

    async def switch_temperature_callback(self):
        self.config.switch_temp_value()
        self.display.show_temperature_icon()

    async def backlight_callback(self):
        self.display.switch_backlight()

    async def switch_blink_callback(self):
        self.config.switch_blink_time_colon_value()
