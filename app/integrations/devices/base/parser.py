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
        
        # 1. Automatically map keys that match NormalizedReading fields
        for key in NormalizedReading.model_fields.keys():
            if key in payload:
                normalized[key] = payload[key]
                
        # 2. Apply device-specific mappings
        for source_key, target_key in self.key_map.items():
            if source_key in payload:
                normalized[target_key] = payload[source_key]
                
        return NormalizedReading(**normalized)

