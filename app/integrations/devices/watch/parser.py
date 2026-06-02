from app.integrations.devices.base.parser import KeyMapParser


class WatchParser(KeyMapParser):
    key_map = {
        "bpm": "heart_rate",
        "spo2": "spo2",
        "steps": "steps",
        "distance": "distance_meters",
        "activeMinutes": "active_minutes",
    }

