import time

from umqtt.simple import MQTTClient
from constants import mqtt_server, mqtt_prefix
from util import singleton


@singleton
class MQTT:
    def __init__(self, scheduler):
        self.scheduler = scheduler
        self.lastping = 0
        self.client = MQTTClient(mqtt_prefix+"picow", mqtt_server, user=None,
                                 password=None, keepalive=300, ssl=False, ssl_params={})
        self.connect()
        scheduler.schedule("mqtt-heartbeat", 250, self.heartbeat_callback)
        scheduler.schedule("mqtt-check", 1, self.client.check_msg)

    def connect(self):
        self.client.connect()
        self.heartbeat(True)
        self.client.set_callback(self.mqtt_callback)
        self.client.subscribe()

    def heartbeat_callback(self, first):
        if first:
            self.client.ping()
            self.lastping = time.ticks_ms()
        if time.ticks_diff(time.ticks_ms(), self.lastping) >= 300000:
            self.client.ping()
            self.lastping = time.ticks_ms()
        return

    def mqtt_callback(self, topic, msg):
        t = topic.decode("utf-8").lstrip(mqtt_prefix)
        print(t)
