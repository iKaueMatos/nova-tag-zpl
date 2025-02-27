import configparser
import os

class Config:
    def __init__(self, config_file="config.ini"):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        if os.path.exists(self.config_file):
            config = configparser.ConfigParser()
            config.read(self.config_file)
            return config
        else:
            return configparser.ConfigParser()

    def load_saved_printer(self):
        if "PrinterSettings" in self.config and "selected_printer" in self.config["PrinterSettings"]:
            return self.config["PrinterSettings"]["selected_printer"]
        return None

    def save_printer(self, printer_name):
        if "PrinterSettings" not in self.config:
            self.config["PrinterSettings"] = {}
        self.config["PrinterSettings"]["selected_printer"] = printer_name
        with open(self.config_file, "w") as config_file:
            self.config.write(config_file)