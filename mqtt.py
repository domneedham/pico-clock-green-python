import time
import json
from configuration import Configuration
from constants import SCHEDULER_MQTT_CHECK, SCHEDULER_MQTT_HEARTBEAT, SCHEDULER_MQTT_STATE
from scheduler import Scheduler
from util import singleton


@singleton
class MQTT:
    class MQTT_Callback:
        def __init__(self, topic: str, callback: function) -> None:
            self.topic = topic
            self.callback = callback

    class MQTT_State:
        def __init__(self, name: str, callback: function) -> None:
            self.name = name
            self.callback = callback

    def __init__(self, scheduler: Scheduler):
        self.scheduler = scheduler
        self.lastping = 0
        self.registered_callbacks = []
        self.state_callbacks = []
        self.configuration = Configuration().mqtt_config
        if self.configuration.enabled:
            from umqtt.simple import MQTTClient

            if self.configuration.username != "":
                user = self.configuration.username
            else:
                user = None
            if self.configuration.password != "":
                password = self.configuration.password
            else:
                password = None

            self.client = MQTTClient(self.configuration.prefix, self.configuration.broker, user=user,
                                     password=password, keepalive=300, ssl=False, ssl_params={})
            self.connect()
            scheduler.schedule(SCHEDULER_MQTT_HEARTBEAT, 250,
                               self.scheduler_heartbeat_callback)
            scheduler.schedule(SCHEDULER_MQTT_CHECK, 1,
                               self.scheduler_mqtt_callback)
            scheduler.schedule(SCHEDULER_MQTT_STATE, 60000,
                               self.scheduler_mqtt_state)

    def connect(self):
        print("Connecting to MQTT")
        self.client.connect()
        self.heartbeat(True)
        self.client.set_callback(self.mqtt_callback)
        topic = self.configuration.prefix + "#"
        self.client.subscribe(topic)
        print("Subscribed to " + topic)

    def heartbeat(self, first=False):
        if first:
            self.client.ping()
            self.lastping = time.ticks_ms()
        if time.ticks_diff(time.ticks_ms(), self.lastping) >= 300000:
            self.client.ping()
            self.lastping = time.ticks_ms()
        return

    async def scheduler_heartbeat_callback(self):
        self.heartbeat(False)

    async def scheduler_mqtt_callback(self):
        self.client.check_msg()

    async def scheduler_mqtt_state(self):
        self.send_state()

    def mqtt_callback(self, topic, msg):
        t = topic.decode().lstrip(mqtt_prefix)
        for c in self.registered_callbacks:
            if t == c.topic:
                c.callback(topic, msg)

    def send_event(self, topic: str, msg: str):
        topic = mqtt_prefix + topic
        self.client.publish(topic, msg)

    def send_state(self):
        self.client.publish(mqtt_base_topic, self.build_state())

    def build_state(self):
        state = dict()
        for s in self.state_callbacks:
            item_name = s.name
            item_state = s.callback()
            state[item_name] = item_state
        return json.dumps(state)

    def register_topic_callback(self, topic, callback):
        self.registered_callbacks.append(self.MQTT_Callback(topic, callback))

    def register_state_callback(self, name, callback):
        self.state_callbacks.append(self.MQTT_State(name, callback))
