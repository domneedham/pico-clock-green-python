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
        self.config = read_json_file("config.json")
        self.update_config_variables()

    def update_config_variables(self):
        self.blink_time_colon = self.config["runConfig"]["blinkTimeColon"]
        self.temp = self.config["runConfig"]["temp"]
        self.clock_type = self.config["runConfig"]["clockType"]
        self.autolight = self.config["runConfig"]["autolight"]

        self.wifi_config = self.WifiConfiguration(
            enabled=self.config["wifiConfig"]["enabled"],
            ssid=self.config["wifiConfig"]["ssid"],
            passphrase=self.config["wifiConfig"]["passphrase"]
        )

        self.mqtt_config = self.MQTTConfiguration(
            enabled=self.config["mqttConfig"]["enabled"],
            broker=self.config["mqttConfig"]["broker"],
            prefix=self.config["mqttConfig"]["prefix"]
        )

    def write_config_file(self):
        write_json_file("config.json", self.config)
        self.update_config_variables()

    def switch_blink_time_colon_value(self):
        if self.config["runConfig"]["blinkTimeColon"]:
            self.config["runConfig"]["blinkTimeColon"] = False
        else:
            self.config["runConfig"]["blinkTimeColon"] = True

        self.write_config_file()

    def switch_temp_value(self):
        if self.config["runConfig"]["temp"] == "c":
            self.config["runConfig"]["temp"] = "f"
        else:
            self.config["runConfig"]["temp"] = "c"

        self.write_config_file()

    def update_clock_type_value(self, value):
        self.config["runConfig"]["clockType"] = value
        self.write_config_file()

    def update_autolight_value(self, value):
        self.config["runConfig"]["autolight"] = value
        self.write_config_file()
