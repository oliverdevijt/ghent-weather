import sys, os, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from generate import wmo_icon

def test_clear_sky():
    assert wmo_icon(0) == "☀️"

def test_mainly_clear():
    assert wmo_icon(1) == "🌤️"

def test_partly_cloudy():
    assert wmo_icon(2) == "⛅"

def test_overcast():
    assert wmo_icon(3) == "☁️"

def test_fog():
    assert wmo_icon(45) == "🌫️"

def test_drizzle():
    assert wmo_icon(51) == "🌦️"

def test_rain():
    assert wmo_icon(61) == "🌧️"

def test_heavy_rain():
    assert wmo_icon(65) == "🌧️"

def test_snow():
    assert wmo_icon(71) == "❄️"

def test_thunderstorm():
    assert wmo_icon(95) == "⛈️"

def test_unknown_code_falls_back():
    assert wmo_icon(999) == "🌡️"


from datetime import date
from generate import build_ics, parse_sequences


def test_parse_sequences_empty_on_missing_file():
    assert parse_sequences("/nonexistent/path.ics") == {}


def test_parse_sequences_roundtrip():
    ics = build_ics([(date(2026, 6, 18), 22, 0)])
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ics", delete=False) as f:
        f.write(ics)
        path = f.name
    result = parse_sequences(path)
    uid = "ghent-weather-2026-06-18@oliverdevijt.github.io"
    assert uid in result
    assert result[uid] == (0, "☀️ 22°C")

def test_ics_contains_vcalendar_wrapper():
    ics = build_ics([])
    assert ics.startswith("BEGIN:VCALENDAR")
    assert ics.strip().endswith("END:VCALENDAR")

def test_ics_method_publish():
    ics = build_ics([])
    assert "METHOD:PUBLISH" in ics

def test_ics_single_event_summary():
    ics = build_ics([(date(2026, 6, 18), 22, 0)])
    assert "SUMMARY:☀️ 22°C" in ics

def test_ics_single_event_uid():
    ics = build_ics([(date(2026, 6, 18), 22, 0)])
    assert "UID:ghent-weather-2026-06-18@oliverdevijt.github.io" in ics

def test_ics_single_event_dtstart():
    ics = build_ics([(date(2026, 6, 18), 22, 0)])
    assert "DTSTART;VALUE=DATE:20260618" in ics

def test_ics_single_event_dtend_next_day():
    ics = build_ics([(date(2026, 6, 18), 22, 0)])
    assert "DTEND;VALUE=DATE:20260619" in ics

def test_ics_last_modified_present():
    ics = build_ics([(date(2026, 6, 18), 22, 0)])
    assert "LAST-MODIFIED:" in ics

def test_ics_sequence_zero_on_first_write():
    ics = build_ics([(date(2026, 6, 18), 22, 0)])
    assert "SEQUENCE:0" in ics

def test_ics_sequence_increments_on_change():
    uid = "ghent-weather-2026-06-18@oliverdevijt.github.io"
    prev = {uid: (0, "☀️ 20°C")}
    ics = build_ics([(date(2026, 6, 18), 22, 0)], prev)
    assert "SEQUENCE:1" in ics

def test_ics_sequence_stable_when_unchanged():
    uid = "ghent-weather-2026-06-18@oliverdevijt.github.io"
    prev = {uid: (2, "☀️ 22°C")}
    ics = build_ics([(date(2026, 6, 18), 22, 0)], prev)
    assert "SEQUENCE:2" in ics

def test_ics_fourteen_events():
    from datetime import timedelta
    start = date(2026, 6, 18)
    days = [(start + timedelta(days=i), 20 + i, 0) for i in range(14)]
    ics = build_ics(days)
    assert ics.count("BEGIN:VEVENT") == 14


from unittest.mock import patch, MagicMock
import json
from generate import fetch_forecast

MOCK_RESPONSE = {
    "daily": {
        "time": ["2026-06-18", "2026-06-19"],
        "temperature_2m_max": [21.4, 18.9],
        "weathercode": [1, 61],
    }
}

def test_fetch_forecast_returns_parsed_tuples():
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps(MOCK_RESPONSE).encode()
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)

    with patch("urllib.request.urlopen", return_value=mock_resp):
        result = fetch_forecast(51.05, 3.72, days=2)

    assert len(result) == 2
    assert result[0] == (date(2026, 6, 18), 21, 1)
    assert result[1] == (date(2026, 6, 19), 19, 61)
