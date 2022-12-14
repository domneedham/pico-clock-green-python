from constants import CONFIGURATION_FILE, CONFIGURATION_RUN_AUTOLIGHT, CONFIGURATION_RUN_BLINK_TIME_COLON, CONFIGURATION_RUN_CLOCK_TYPE, CONFIGURATION_MQTT_BROKER, CONFIGURATION_MQTT_CONFIG, CONFIGURATION_MQTT_ENABLED, CONFIGURATION_MQTT_PREFIX, CONFIGURATION_RUN_CONFIG, CONFIGURATION_RUN_TEMP, CONFIGURATION_WIFI_CONFIG, CONFIGURATION_WIFI_ENABLED, CONFIGURATION_WIFI_PASSPHRASE, CONFIGURATION_WIFI_SSID
from util import singleton
from helpers import read_json_file, write_json_file


@singleton
class Configuration:
    class WifiConfiguration:
        def __init__(self, enabled: bool, ssid: str, passphrase: str) -> None:
            self.enabled = enabled
            self.ssid = ssid
            self.passphrase = passphrase

    class MQTTConfiguration:
        def __init__(self, enabled: bool, broker: str, prefix: str) -> None:
            self.enabled = enabled
            self.broker = broker
            self.prefix = prefix
            self.base_topic = prefix + "/"

    def __init__(self) -> None:
        self.config = {}
        self.blink_time_colon = False
        self.temp = "c"
        self.clock_type = "24"
        self.autolight = False
        self.read_config_file()

    def read_config_file(self):
        self.config = read_json_file(CONFIGURATION_FILE)
        self.update_config_variables()

    def update_config_variables(self):
        self.blink_time_colon = self.config[CONFIGURATION_RUN_CONFIG][CONFIGURATION_RUN_BLINK_TIME_COLON]
        self.temp = self.config[CONFIGURATION_RUN_CONFIG][CONFIGURATION_RUN_TEMP]
        self.clock_type = self.config[CONFIGURATION_RUN_CONFIG][CONFIGURATION_RUN_CLOCK_TYPE]
        self.autolight = self.config[CONFIGURATION_RUN_CONFIG][CONFIGURATION_RUN_AUTOLIGHT]

        self.wifi_config = self.WifiConfiguration(
            enabled=self.config[CONFIGURATION_WIFI_CONFIG][CONFIGURATION_WIFI_ENABLED],
            ssid=self.config[CONFIGURATION_WIFI_CONFIG][CONFIGURATION_WIFI_SSID],
            passphrase=self.config[CONFIGURATION_WIFI_CONFIG][CONFIGURATION_WIFI_PASSPHRASE]
        )

        self.mqtt_config = self.MQTTConfiguration(
            enabled=self.config[CONFIGURATION_MQTT_CONFIG][CONFIGURATION_MQTT_ENABLED],
            broker=self.config[CONFIGURATION_MQTT_CONFIG][CONFIGURATION_MQTT_BROKER],
            prefix=self.config[CONFIGURATION_MQTT_CONFIG][CONFIGURATION_MQTT_PREFIX]
        )

    def write_config_file(self):
        write_json_file(CONFIGURATION_FILE, self.config)
        self.update_config_variables()

    def switch_blink_time_colon_value(self):
        if self.config[CONFIGURATION_RUN_CONFIG][CONFIGURATION_RUN_BLINK_TIME_COLON]:
            self.config[CONFIGURATION_RUN_CONFIG][CONFIGURATION_RUN_BLINK_TIME_COLON] = False
        else:
            self.config[CONFIGURATION_RUN_CONFIG][CONFIGURATION_RUN_BLINK_TIME_COLON] = True

        self.write_config_file()

    def switch_temp_value(self):
        if self.config[CONFIGURATION_RUN_CONFIG][CONFIGURATION_RUN_TEMP] == "c":
            self.config[CONFIGURATION_RUN_CONFIG][CONFIGURATION_RUN_TEMP] = "f"
        else:
            self.config[CONFIGURATION_RUN_CONFIG][CONFIGURATION_RUN_TEMP] = "c"

        self.write_config_file()

    def update_clock_type_value(self, value):
        self.config[CONFIGURATION_RUN_CONFIG][CONFIGURATION_RUN_CLOCK_TYPE] = value
        self.write_config_file()

    def update_autolight_value(self, value):
        self.config[CONFIGURATION_RUN_CONFIG][CONFIGURATION_RUN_AUTOLIGHT] = value
        self.write_config_file()
