import json
import random
import re
import time
from datetime import date as dt_date
from typing import Dict

import requests
from bs4 import BeautifulSoup
from langchain_core.tools import tool
from loguru import logger

from app.cache import r

# ---------- Cache Helpers ----------

def _cache_get(key: str):
    try:
        if r.exists(key):
            raw = r.get(key)
            return json.loads(raw) if raw else None
    except Exception as e:
        logger.warning(f"cache get failed: {e}")
    return None


def _cache_set(key: str, value, ttl: int):
    try:
        r.setex(key, ttl, json.dumps(value))
    except Exception as e:
        logger.error(f"cache set failed: {e}")


# ---------- HTTP Session ----------

def _get_session():
    s = requests.Session()
    s.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    })
    return s


# ---------- Location Lookup ----------

def get_place_id_from_coords(city: str) -> str | None:
    """Resolve Weather.com placeId from latitude/longitude with caching."""
    key = f"placeid:{city}"
    cached = _cache_get(key)
    if cached:
        return cached
    
    url = "https://weather.com/api/v1/p/redux-dal"
    payload = [
        {
            "name": "getSunV3LocationSearchUrlConfig",
            "params": {
                "query": f"{city}",
                "language": "en-US",
                "locationType": "locale",
            },
        }
    ]
    try:
        resp = requests.post(url, json=payload, headers={"content-type": "application/json"})
        resp.raise_for_status()
        data = resp.json()
        # Extract first placeId
        obj = list(data["dal"]["getSunV3LocationSearchUrlConfig"].values())[0]
        place_id = obj["data"]["location"]["placeId"][0]

        # Cache for 7 days (604800s)
        _cache_set(key, place_id, 604800)
        return place_id
    except Exception as e:
        logger.error(f"Failed to fetch placeId for {city}: {e}")
        return None


# ---------- Parsers ----------

def _parse_num(text: str, default: float = 0.0) -> float:
    if not text:
        return default
    m = re.search(r"-?\d+", text)
    return float(m.group()) if m else default


def _parse_temp_c(text: str) -> float:
    t = _parse_num(text, 20.0)
    if t > 50 or (text and 'f' in text.lower()):
        t = (t - 32) * 5 / 9
    return round(float(t), 2)


def _parse_percent(text: str) -> int:
    m = re.search(r"(\d+)%", text or "")
    if m:
        return int(m.group(1))
    m2 = re.search(r"\d+", text or "")
    return int(m2.group()) if m2 else 0


def _parse_wind_kmh(text: str) -> float:
    sp = _parse_num(text, 10.0)
    if text and 'mph' in text.lower():
        sp *= 1.60934
    return float(sp)


def _condition_to_code(desc: str) -> int:
    d = (desc or '').lower()
    if any(w in d for w in ['clear', 'sunny']):
        return 0
    if 'partly' in d or 'mostly sunny' in d:
        return 1
    if any(w in d for w in ['cloudy', 'overcast']):
        return 3
    if 'rain' in d:
        return 63
    if 'snow' in d:
        return 73
    if 'storm' in d or 'thunder' in d:
        return 95
    return 2


# ---------- Scrape Weather.com ----------

def _extract_current(soup: BeautifulSoup) -> Dict | None:
    try:
        temp_el = soup.find('span', {'data-testid': 'TemperatureValue'}) or soup.find('span', class_=re.compile('temp', re.I))
        cond_el = soup.find('div', {'data-testid': 'wxPhrase'}) or soup.find('div', class_=re.compile('phrase', re.I))
        page_text = soup.get_text(separator=' ')

        humidity = 50
        hm = re.search(r"humidity\s*:?\s*(\d+)%", page_text, re.I)
        if hm:
            humidity = int(hm.group(1))

        wind_kmh = 10.0
        wm = re.search(r"wind\s*:?\s*(\d+)\s*(mph|km)\w*", page_text, re.I)
        if wm:
            wind_kmh = _parse_wind_kmh(wm.group(0))

        cond = cond_el.get_text(strip=True) if cond_el else "Unknown"
        temp_c = _parse_temp_c(temp_el.get_text() if temp_el else "Unknown°")

        return {
            'temperature_c': temp_c,
            'temperature_f': temp_c * 9/5 + 32,
            'condition': cond,
            'condition_code': _condition_to_code(cond),
            'humidity': humidity,
            'wind_kmh': wind_kmh,
        }
    except Exception as e:
        logger.warning(f"current parse failed: {e}")
        return None


def _extract_forecast(soup: BeautifulSoup) -> list[dict] | None:
    try:
        cards = soup.find_all("div", {"data-testid": "DetailsSummary"})
        if not cards:
            logger.warning("No forecast cards found")
            return []

        forecast = []
        for card in cards:
            try:
                day = card.find("h2", {"data-testid": "daypartName"})
                condition = card.find("span", class_="DetailsSummary--wxPhrase--nhYpy")
                temps = card.find_all("span", {"data-testid": "TemperatureValue"})
                precip = card.find("span", {"data-testid": "PercentageValue"})
                wind = card.find("div", {"data-testid": "wind"})

                # Parse values
                condition_code = _condition_to_code(condition.get_text(strip=True)) if condition else None
                temps_high_c = _parse_temp_c(temps[0].get_text(strip=True)) if len(temps) > 0 else None
                temps_low_c = _parse_temp_c(temps[1].get_text(strip=True)) if len(temps) > 1 else None
                precip_pct = _parse_percent(precip.get_text(strip=True)) if precip else None
                wind_kmh = _parse_wind_kmh(wind.get_text(strip=True)) if wind else None

                forecast.append({
                    "day": day.get_text(strip=True) if day else None,
                    "date": day.get_text(strip=True) if day else None,
                    "condition": condition.get_text(strip=True) if condition else None,
                    "condition_code": condition_code,
                    "temp_high_c": temps_high_c,
                    "temp_low_c": temps_low_c,
                    "precip": precip_pct,
                    "wind_kmh": wind_kmh,
                })
            except Exception as e:
                logger.debug(f"Skipping one forecast card: {e}")
                continue

        return forecast
    except Exception as e:
        logger.error(f"Failed to parse forecast: {e}")
        return []


def get_weather_data(city: str) -> Dict:
    """Unified fetch: current + 10-day forecast; cached for 6h per city-date."""
    today = dt_date.today().strftime('%Y-%m-%d')
    key = f"weather:{city.lower()}:{today}"
    cached = _cache_get(key)
    if cached:
        return cached

    loc = get_place_id_from_coords(city)
    if not loc:
        logger.error(f"No weather.com location found for {city}")
        return {"error": f"City '{city}' not found on Weather.com"}
    
    session = _get_session()
    url = f"https://weather.com/weather/tenday/l/{loc}"
    try:
        time.sleep(random.uniform(0.5, 1.0))
        resp = session.get(url, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, 'html.parser')        
        current = _extract_current(soup)
        forecast = _extract_forecast(soup)
        data = {'city': city, 'date_retrieved': today, 'current': current, 'forecast': forecast}
        _cache_set(key, data, 21600)  # 6h
        return data
    except Exception as e:
        logger.error(f"weather fetch failed for {city}: {e}")
        return {"error": "not found", "city": city}


# ---------- LangChain Tools ----------

@tool
def get_current_weather_tool(city: str) -> str:
    """Return formatted current weather for a city."""
    data = get_weather_data(city)
    if "error" in data:
        return f"Weather not found for {city}"
    c = data['current']
    return (
        f"Current weather in {data['city']}\n"
        f"Temp: {c['temperature_c']:.1f}°C ({c['temperature_f']:.1f}°F)\n"
        f"Condition: {c['condition']}\n"
        f"Humidity: {c['humidity']}% | Wind: {c['wind_kmh']:.0f} km/h"
    )


@tool
def get_weather_forecast_tool(city: str, days: int = 5) -> str:
    """Return a formatted {1..10}-day forecast for a city."""
    days = max(1, min(10, int(days)))
    data = get_weather_data(city)
    if "error" in data:
        return f"Weather not found for {city}"
    f = data['forecast']
    if len(f) == 0:
        return f"No forecast available for {city}."
    out = [f"{days}-day forecast for {data['city']}:"]
    for d in f[:days]:
        out.append(
            f"{d['date']}: {d['condition']}, H {d['temp_high_c']:.0f}°C / L {d['temp_low_c']:.0f}°C, Rain {d['precip']}%, Wind {d['wind_kmh']:.0f} km/h"
        )
    return "\n".join(out)


@tool
def get_weather_summary_tool(city: str) -> str:
    """Return a compact current + 3-day summary."""
    data = get_weather_data(city)
    if "error" in data:
        return f"Weather not found for {city}"
    c = data['current']
    f = data['forecast'][:3]
    lines = [
        f"Weather Summary for {data['city']}",
        f"• Now: {c['condition']} — {c['temperature_c']:.1f}°C ({c['temperature_f']:.1f}°F), Humidity {c['humidity']}%, Wind {c['wind_kmh']:.0f} km/h",
        "• Next 3 days:",
    ]
    for d in f:
        lines.append(
            f"  - {d['date']}: {d['condition']}, H {d['temp_high_c']:.0f}°C / L {d['temp_low_c']:.0f}°C, Rain {d['precip']}%, Wind {d['wind_kmh']:.0f} km/h"
        )
    return "\n".join(lines)




