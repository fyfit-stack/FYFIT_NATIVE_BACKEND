from app.integrations.devices.base.parser import DevicePayloadParser
from app.integrations.devices.sr16.parser import Sr16Parser
from app.integrations.devices.syo1.parser import Syo1Parser
from app.integrations.devices.watch.parser import WatchParser
from app.integrations.devices.y65.parser import Y65Parser

DEVICE_REGISTRY: dict[str, type[DevicePayloadParser]] = {
    "SYO1": Syo1Parser,
    "SR16": Sr16Parser,
    "Y65": Y65Parser,
    "WATCH": WatchParser,
}


def get_parser(model: str) -> DevicePayloadParser:
    parser_cls = DEVICE_REGISTRY.get(model.upper())
    if parser_cls is None:
        return Syo1Parser()
    return parser_cls()

