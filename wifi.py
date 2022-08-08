import network
import time
from configuration import wlan_id, wlan_password
from util import singleton


@singleton
class WLAN:
    def __init__(self, scheduler):
        self.scheduler = scheduler
        self.wlan = None
        self.connect_to_wifi()

    def connect_to_wifi(self):
        print("Connecting to WiFi")
        self.wlan = network.WLAN(network.STA_IF)

        self.wlan.active(True)
        self.wlan.config(pm=0xa11140)  # Disable powersave mode
        self.wlan.connect(wlan_id, wlan_password)

        # Wait for connect or fail
        max_wait = 10
        while max_wait > 0:
            if self.wlan.status() < 0 or self.wlan.status() >= 3:
                break
            max_wait -= 1
            print('Waiting for connection...')
            time.sleep(1)

        # Handle connection error
        if self.wlan.status() != 3:
            raise RuntimeError('WiFi connection failed')
        else:
            status = self.wlan.ifconfig()
            print('IP = ' + status[0])
