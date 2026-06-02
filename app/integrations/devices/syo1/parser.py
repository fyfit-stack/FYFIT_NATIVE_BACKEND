from app.integrations.devices.base.parser import KeyMapParser


class Syo1Parser(KeyMapParser):
    key_map = {
        "hr": "heart_rate",
        "spo2": "spo2",
        "steps": "steps",
        "stress": "stress",
        "temp": "skin_temperature_celsius",
    }

