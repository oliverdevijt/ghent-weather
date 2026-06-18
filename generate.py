import urllib.request
import json
from datetime import date, timedelta, datetime, timezone


def wmo_icon(code: int) -> str:
    if code == 0:
        return "☀️"
    if code == 1:
        return "🌤️"
    if code == 2:
        return "⛅"
    if code == 3:
        return "☁️"
    if code in (45, 48):
        return "🌫️"
    if 51 <= code <= 57:
        return "🌦️"
    if 61 <= code <= 67:
        return "🌧️"
    if 71 <= code <= 77:
        return "❄️"
    if 80 <= code <= 82:
        return "🌦️"
    if 85 <= code <= 86:
        return "❄️"
    if code in (95, 96, 99):
        return "⛈️"
    return "🌡️"


def build_ics(forecast: list[tuple[date, int, int]]) -> str:
    now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//oliverdevijt//ghent-weather//EN",
        "CALSCALE:GREGORIAN",
        "X-WR-CALNAME:Ghent Weather",
        "X-WR-TIMEZONE:Europe/Brussels",
    ]
    for day, temp_max, code in forecast:
        dtstart = day.strftime("%Y%m%d")
        dtend = (day + timedelta(days=1)).strftime("%Y%m%d")
        uid = f"ghent-weather-{day.isoformat()}@oliverdevijt.github.io"
        icon = wmo_icon(code)
        lines += [
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{now}",
            f"DTSTART;VALUE=DATE:{dtstart}",
            f"DTEND;VALUE=DATE:{dtend}",
            f"SUMMARY:{icon} {temp_max}°C",
            "END:VEVENT",
        ]
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"


def fetch_forecast(lat: float, lon: float, days: int = 14) -> list[tuple[date, int, int]]:
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&daily=temperature_2m_max,weathercode"
        f"&forecast_days={days}"
        f"&timezone=Europe%2FBrussels"
    )
    with urllib.request.urlopen(url, timeout=30) as resp:
        data = json.loads(resp.read())

    daily = data["daily"]
    return [
        (date.fromisoformat(d), round(t), c)
        for d, t, c in zip(
            daily["time"],
            daily["temperature_2m_max"],
            daily["weathercode"],
        )
    ]


def main() -> None:
    forecast = fetch_forecast(51.05, 3.72, days=14)
    ics = build_ics(forecast)
    with open("weather.ics", "w", encoding="utf-8", newline="") as f:
        f.write(ics)
    print(f"Written {len(forecast)} events to weather.ics")


if __name__ == "__main__":
    main()
