from app.integrations.devices.base.parser import KeyMapParser


class Y65Parser(KeyMapParser):
    key_map = {
        "heart_rate": "heart_rate",
        "oxygen": "spo2",
        "step_count": "steps",
        "calories": "calories_kcal",
    }

