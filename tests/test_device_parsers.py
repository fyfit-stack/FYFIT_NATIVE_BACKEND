from datetime import datetime, timezone

from app.integrations.devices.registry import get_parser


def test_syo1_parser_normalizes_payload():
    parser = get_parser("SYO1")
    reading = parser.normalize_reading(
        datetime(2026, 6, 2, tzinfo=timezone.utc),
        {"hr": 78, "spo2": 98, "steps": 5000, "stress": 20},
    )

    assert reading.heart_rate == 78
    assert reading.spo2 == 98
    assert reading.steps == 5000
    assert reading.stress == 20


def test_sr16_parser_normalizes_payload():
    parser = get_parser("SR16")
    reading = parser.normalize_reading(
        datetime(2026, 6, 2, tzinfo=timezone.utc),
        {"heartRate": 78, "bloodOxygen": 98},
    )

    assert reading.heart_rate == 78
    assert reading.spo2 == 98

