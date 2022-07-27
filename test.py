from rtc import RTC
from display import Display
from scheduler import Scheduler
scheduler = Scheduler()
dis = Display(scheduler)
scheduler.start()
clock = RTC()
