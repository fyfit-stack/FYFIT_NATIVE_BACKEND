from abc import ABC, abstractmethod
from datetime import datetime

from app.schemas.sync import NormalizedReading


class DevicePayloadParser(ABC):
    @abstractmethod
    def normalize_reading(self, recorded_at: datetime, payload: dict) -> NormalizedReading:
        raise NotImplementedError


class KeyMapParser(DevicePayloadParser):
    key_map: dict[str, str] = {}

    def normalize_reading(self, recorded_at: datetime, payload: dict) -> NormalizedReading:
        normalized = {"recorded_at": recorded_at, "source_payload": payload}
        for source_key, target_key in self.key_map.items():
            if source_key in payload:
                normalized[target_key] = payload[source_key]
        return NormalizedReading(**normalized)

