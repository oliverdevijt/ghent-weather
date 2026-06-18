import sys, os
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
