import network
import time
from constants import wlan_id, wlan_password


def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)

    wlan.active(True)
    wlan.config(pm=0xa11140)  # Disable powersave mode
    wlan.connect(wlan_id, wlan_password)

    # Wait for connect or fail
    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print('waiting for connection...')
        time.sleep(1)

    # Handle connection error
    if wlan.status() != 3:
        raise RuntimeError('WiFi connection failed')
    else:
        print('connected')
        status = wlan.ifconfig()
        print('ip = ' + status[0])

    return wlan
