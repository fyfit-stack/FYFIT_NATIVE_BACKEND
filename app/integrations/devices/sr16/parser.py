from app.integrations.devices.base.parser import KeyMapParser


class Sr16Parser(KeyMapParser):
    key_map = {
        "heartRate": "heart_rate",
        "bloodOxygen": "spo2",
        "hrv": "hrv",
        "stressScore": "stress",
    }

