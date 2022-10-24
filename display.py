from machine import Pin, ADC, Timer
from constants import SCHEDULER_ANIMATION, SCHEDULER_ENABLE_LEDS, SCHEDULER_UPDATE_BACKLIGHT_VALUE
import uasyncio

from util import partial, singleton
from utime import sleep, sleep_ms, sleep_us
from configuration import Configuration
import helpers


@singleton
class Display:
    class WaitForAnimation:
        def __init__(self, callback, *args, **kwargs) -> None:
            self.callback = partial(callback, *args, **kwargs)

    def __init__(self, scheduler):
        self.a0 = Pin(16, Pin.OUT)
        self.a1 = Pin(18, Pin.OUT)
        self.a2 = Pin(22, Pin.OUT)
        self.oe = Pin(13, Pin.OUT)
        self.sdi = Pin(11, Pin.OUT)
        self.clk = Pin(10, Pin.OUT)
        self.le = Pin(12, Pin.OUT)
        self.ain = ADC(26)

        self.row = 0
        self.leds = [[0] * 32 for i in range(0, 8)]
        self.animating = False
        self.showing_time = False
        self.display_text_width = 32
        self.disp_offset = 2
        self.display_queue = []
        self.display_queue_timer = Timer(-1)
        self.initialise_fonts()
        self.initialise_icons()
        self.initialise_days()

        self.scheduler = scheduler
        self.config = Configuration()

        self.initialise_backlight()
        self.show_temperature_icon()
        self.scheduler.schedule(SCHEDULER_ENABLE_LEDS, 0, self.enable_leds)

    def enable_leds(self):
        self.row = (self.row + 1) % 8
        led_row = self.leds[self.row]
        for col in range(32):
            self.clk.value(0)
            self.sdi.value(led_row[col])
            self.clk.value(1)
        self.le.value(1)
        self.le.value(0)

        self.a0.value(1 if self.row & 0x01 else 0)
        self.a1.value(1 if self.row & 0x02 else 0)
        self.a2.value(1 if self.row & 0x04 else 0)
        self.oe.value(0)
        sleep_us(self.backlight_sleep[self.current_backlight])
        self.oe.value(1)

    async def animate_text(self, text: str, delay=1000, clear=True):
        if self.animating:
            self.display_queue.append(
                self.WaitForAnimation(self.animate_text, text, delay, clear=clear))
            return

        # add blank whitespace for text to show correctly
        text = text + " "
        if clear:
            self.clear_text()
        await self.show_text(text)
        self.animate(delay)

    def animate(self, delay=1000):
        self.runs = 0
        self.animating = True
        self.scheduler.schedule(
            SCHEDULER_ANIMATION, 200, self.scroll_text_left, delay)

    async def scroll_text_left(self):
        for row in range(8):
            led_row = self.leds[row]
            for col in range(self.display_text_width):
                if row > 0 and col > 2:
                    self.leds[row][col-1] = led_row[col]
        self.runs += 1

        if self.runs == self.display_text_width - 5:  # account for whitespace
            self.animating = False
            self.scheduler.remove(SCHEDULER_ANIMATION)
            await self.process_callback_queue()

    async def process_callback_queue(self, *args):
        if len(self.display_queue) == 0:
            if not self.showing_time:
                await self.show_time()
        else:
            await self.display_queue[0].callback()
            self.display_queue.pop(0)

    def clear(self, x=0, y=0, w=24, h=7):
        self.display_text_width = 0
        for yy in range(y, y + h + 1):
            for xx in range(x, x + w + 1):
                self.leds[yy][xx] = 0

    def clear_text(self):
        self.animating = False
        self.scheduler.remove(SCHEDULER_ANIMATION)
        self.clear(x=2, y=1, w=24, h=6)

    def reset(self):
        self.clear_text()
        self.display_queue = []

    def show_char(self, character, pos):
        pos += self.disp_offset  # Plus the offset of the status indicator
        char = self.ziku[character]
        for row in range(1, 8):
            byte = char.rows[row - 1]
            for col in range(0, char.width):
                self.leds[row][pos + col] = (byte >> col) % 2

    async def show_text_for_period(self, text, pos=0, clear=True, display_period=5000):
        if self.animating:
            self.display_queue.append(
                self.WaitForAnimation(self.show_text_for_period, text, pos, display_period))
            return

        await self.show_text(text, pos, clear)
        await uasyncio.sleep_ms(display_period)
        await self.process_callback_queue()
        # self.display_queue_timer.init(period=display_period, mode=Timer.ONE_SHOT,
        #                               callback=self.process_callback_queue)

    async def show_text(self, text, pos=0, clear=True):
        if self.animating:
            self.display_queue.append(
                self.WaitForAnimation(self.show_text, text, pos))
            return

        if clear:
            self.clear_text()

        i = 0
        while i < len(text):
            if text[i:i + 2] in self.ziku:
                c = text[i:i + 2]
                i += 2
            else:
                c = text[i]
                i += 1
            width = self.ziku[c].width
            self.display_text_width += width
        # account for whitespace between text words
        self.display_text_width += len(text) + 1

        # handle small text by resetting back to 32
        if self.display_text_width < 32:
            self.display_text_width = 32
        self.set_new_led_rows()

        i = 0
        while i < len(text):
            if text[i:i + 2] in self.ziku:
                c = text[i:i + 2]
                i += 2
            else:
                c = text[i]
                i += 1
            self.show_char(c, pos)
            width = self.ziku[c].width
            pos += width + 1

    async def show_time(self, time=None, display_period=5000):
        self.showing_time = True
        if time != None:
            self.time = time
        await self.show_text_for_period(self.time, display_period=display_period)

    async def show_temperature(self, temp):
        self.showing_time = False
        symbol = ""
        if self.config.temp == "c":
            symbol = "°C"
        else:
            temp = helpers.convert_celsius_to_temperature(temp)
            symbol = "°F"
        temp = str(temp)
        await self.animate_text(self.time + " " + temp +
                                symbol, delay=0, clear=False)

    async def show_message(self, text: str):
        self.showing_time = False
        await self.show_text_for_period(text, display_period=8000)

    def show_icon(self, name):
        icon = self.Icons[name]
        for w in range(icon.width):
            self.leds[icon.y][icon.x + w] = 1

    def hide_icon(self, name):
        icon = self.Icons[name]
        for w in range(icon.width):
            self.leds[icon.y][icon.x + w] = 0

    def set_new_led_rows(self):
        # copy days of week led row
        day_of_week_row = self.leds[0]
        icon_column_one = []
        icon_column_two = []
        # copy column 1 and two (icons)
        for row in range(1, 9):
            icon_column_one.append(self.leds[row - 1][0])
            icon_column_two.append(self.leds[row - 1][1])

        # reset led array to use new display width (allows for text bigger than screen)
        new_leds = [[0] * self.display_text_width for i in range(0, 8)]

        # put back previously captured values as they were reset in led reset
        new_leds[0] = day_of_week_row
        for row in range(1, 9):
            new_leds[row - 1][0] = icon_column_one[row - 1]
            new_leds[row - 1][1] = icon_column_two[row - 1]

        self.leds = new_leds

    def sidelight_on(self):
        self.leds[0][2] = 1
        self.leds[0][5] = 1

    def sidelight_off(self):
        self.leds[0][2] = 0
        self.leds[0][5] = 0

    def switch_backlight(self):
        if self.auto_backlight:
            self.auto_backlight = False
            self.hide_icon("AutoLight")
            self.current_backlight = 0
            self.scheduler.remove(
                SCHEDULER_UPDATE_BACKLIGHT_VALUE)
            self.config.update_autolight_value(False)
        elif self.current_backlight == 3:
            self.show_icon("AutoLight")
            self.auto_backlight = True
            self.update_auto_backlight_value()
            self.scheduler.schedule(
                SCHEDULER_UPDATE_BACKLIGHT_VALUE, 1000, self.update_backlight_callback)
            self.config.update_autolight_value(True)
        else:
            self.current_backlight += 1

    def initialise_backlight(self):
        # CPU freq needs to be increase to 250 for better results
        # From 10 (low) to 1500(High)
        self.backlight_sleep = [10, 100, 300, 1500]
        self.current_backlight = 3
        self.auto_backlight = self.config.autolight
        self.update_auto_backlight_value()

        if self.auto_backlight:
            self.show_icon("AutoLight")
            self.scheduler.schedule(
                SCHEDULER_UPDATE_BACKLIGHT_VALUE, 1000, self.update_backlight_callback)

    def update_auto_backlight_value(self):
        aim = self.ain.read_u16()
        if aim > 65000:  # Low light
            self.current_backlight = 0
        elif aim > 60000:
            self.current_backlight = 1
        elif aim > 40000:
            self.current_backlight = 2
        else:
            self.current_backlight = 3

    async def update_backlight_callback(self):
        self.update_auto_backlight_value()

    def show_temperature_icon(self):
        if self.config.temp == "c":
            self.show_icon("°C")
            self.hide_icon("°F")
        else:
            self.show_icon("°F")
            self.hide_icon("°C")

    def print(self):
        for row in range(0, 8):
            for pos in range(0, 24):
                print("X" if self.leds[row][pos] == 1 else " ", end="")
            print("")

    def square(self):
        '''
        Prints a crossed square. For debugging purposes.
        '''
        for row in range(1, 8):
            self.leds[row][2] = 1
            self.leds[row][23] = 1
        for col in range(2, 23):
            self.leds[1][col] = 1
            self.leds[7][col] = 1
            self.leds[int(col / 24 * 7) + 1][col] = 1
            self.leds[7 - int(col / 24 * 7)][col] = 1

    class Character:
        def __init__(self, width, rows, offset=2):
            self.width = width
            self.rows = rows
            self.offset = offset

    class Icon:
        def __init__(self, x, y, width=1):
            self.x = x
            self.y = y
            self.width = width

    def initialise_icons(self):
        self.Icons = {
            "MoveOn": self.Icon(0, 0, width=2),
            "AlarmOn": self.Icon(0, 1, width=2),
            "CountDown": self.Icon(0, 2, width=2),
            "°F": self.Icon(0, 3),
            "°C": self.Icon(1, 3),
            "AM": self.Icon(0, 4),
            "PM": self.Icon(1, 4),
            "CountUp": self.Icon(0, 5, width=2),
            "Hourly": self.Icon(0, 6, width=2),
            "AutoLight": self.Icon(0, 7, width=2),
            "Mon": self.Icon(3, 0, width=2),
            "Tue": self.Icon(6, 0, width=2),
            "Wed": self.Icon(9, 0, width=2),
            "Thur": self.Icon(12, 0, width=2),
            "Fri": self.Icon(15, 0, width=2),
            "Sat": self.Icon(18, 0, width=2),
            "Sun": self.Icon(21, 0, width=2),
        }

    def initialise_days(self):
        self.days_of_week = {
            1: "Mon",
            2: "Tue",
            3: "Wed",
            4: "Thur",
            5: "Fri",
            6: "Sat",
            7: "Sun"
        }

    def show_day(self, int):
        for key in self.days_of_week:
            if key == int:
                self.show_icon(self.days_of_week[key])
            else:
                self.hide_icon(self.days_of_week[key])

    # Derived from c code created by yufu on 2021/1/23.
    # Modulus method: negative code, reverse, line by line, 4X7 font
    def initialise_fonts(self):
        self.ziku = {
            "all": self.Character(width=3, rows=[0x05, 0x05, 0x03, 0x03, 0x03, 0x03, 0x03]),
            "0": self.Character(width=4, rows=[0x06, 0x09, 0x09, 0x09, 0x09, 0x09, 0x06]),
            "1": self.Character(width=4, rows=[0x04, 0x06, 0x04, 0x04, 0x04, 0x04, 0x0E]),
            "2": self.Character(width=4, rows=[0x06, 0x09, 0x08, 0x04, 0x02, 0x01, 0x0F]),
            "3": self.Character(width=4, rows=[0x06, 0x09, 0x08, 0x06, 0x08, 0x09, 0x06]),
            "4": self.Character(width=4, rows=[0x08, 0x0C, 0x0A, 0x09, 0x0F, 0x08, 0x08]),
            "5": self.Character(width=4, rows=[0x0F, 0x01, 0x07, 0x08, 0x08, 0x09, 0x06]),
            "6": self.Character(width=4, rows=[0x04, 0x02, 0x01, 0x07, 0x09, 0x09, 0x06]),
            "7": self.Character(width=4, rows=[0x0F, 0x09, 0x04, 0x04, 0x04, 0x04, 0x04]),
            "8": self.Character(width=4, rows=[0x06, 0x09, 0x09, 0x06, 0x09, 0x09, 0x06]),
            "9": self.Character(width=4, rows=[0x06, 0x09, 0x09, 0x0E, 0x08, 0x04, 0x02]),
            "A": self.Character(width=4, rows=[0x06, 0x09, 0x09, 0x0F, 0x09, 0x09, 0x09]),
            "B": self.Character(width=4, rows=[0x07, 0x09, 0x09, 0x07, 0x09, 0x09, 0x07]),
            "C": self.Character(width=4, rows=[0x06, 0x09, 0x01, 0x01, 0x01, 0x09, 0x06]),
            "D": self.Character(width=4, rows=[0x07, 0x09, 0x09, 0x09, 0x09, 0x09, 0x07]),
            "E": self.Character(width=4, rows=[0x0F, 0x01, 0x01, 0x0F, 0x01, 0x01, 0x0F]),
            "F": self.Character(width=4, rows=[0x0F, 0x01, 0x01, 0x0F, 0x01, 0x01, 0x01]),
            "G": self.Character(width=4, rows=[0x06, 0x09, 0x01, 0x0D, 0x09, 0x09, 0x06]),
            "H": self.Character(width=4, rows=[0x09, 0x09, 0x09, 0x0F, 0x09, 0x09, 0x09]),
            "I": self.Character(width=3, rows=[0x07, 0x02, 0x02, 0x02, 0x02, 0x02, 0x07]),
            "J": self.Character(width=4, rows=[0x0F, 0x08, 0x08, 0x08, 0x09, 0x09, 0x06]),
            "K": self.Character(width=4, rows=[0x09, 0x05, 0x03, 0x01, 0x03, 0x05, 0x09]),
            "L": self.Character(width=4, rows=[0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x0F]),
            # 5×7
            "M": self.Character(width=4, rows=[0x00, 0x11, 0x1B, 0x15, 0x11, 0x11, 0x11, 0x11]),
            "N": self.Character(width=4, rows=[0x09, 0x09, 0x0B, 0x0D, 0x09, 0x09, 0x09]),
            "O": self.Character(width=4, rows=[0x06, 0x09, 0x09, 0x09, 0x09, 0x09, 0x06]),
            "P": self.Character(width=4, rows=[0x07, 0x09, 0x09, 0x07, 0x01, 0x01, 0x01]),
            # Q
            "Q": self.Character(width=5, rows=[0x0E, 0x11, 0x11, 0x11, 0x15, 0x19, 0x0E]),
            # R
            "R": self.Character(width=4, rows=[0x07, 0x09, 0x09, 0x07, 0x03, 0x05, 0x09]),
            # S
            "S": self.Character(width=4, rows=[0x06, 0x09, 0x02, 0x04, 0x08, 0x09, 0x06]),
            # 5×7
            "T": self.Character(width=5, rows=[0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04]),
            "U": self.Character(width=4, rows=[0x09, 0x09, 0x09, 0x09, 0x09, 0x09, 0x06]),
            # 5×7
            "V": self.Character(width=5, rows=[0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04]),
            # 5×7
            "W": self.Character(width=5, rows=[0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11]),
            "X": self.Character(width=5, rows=[0x11, 0x0A, 0x04, 0x04, 0x04, 0x0A, 0x11]),
            # 5*7
            "Y": self.Character(width=4, rows=[0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04]),
            # 4×7
            "Z": self.Character(width=4, rows=[0x0F, 0x08, 0x04, 0x02, 0x01, 0x0F, 0x00]),

            # 2×7
            ":": self.Character(width=2, rows=[0x00, 0x03, 0x03, 0x00, 0x03, 0x03, 0x00]),
            # colon width space
            " :": self.Character(width=2, rows=[0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
            # temp symbol
            "°": self.Character(width=2, rows=[0x03, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00]),
            # space
            " ": self.Character(width=4, rows=[0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),

            # 1×7
            ".": self.Character(width=1, rows=[0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01]),
            # 2×7
            "-": self.Character(width=2, rows=[0x00, 0x00, 0x00, 0x03, 0x00, 0x00, 0x00]),
            # 3×7
            "/": self.Character(width=2, rows=[0x02, 0x02, 0x02, 0x01, 0x01, 0x01, 0x01, 0x01]),
        }
