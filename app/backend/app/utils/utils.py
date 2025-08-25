from typing import Tuple
from app.utils.constants import SUNNY_CODES

def _desc_sunny(code: int) -> bool:
    return code in SUNNY_CODES


def _meets_prefs(day: dict, prefs: dict) -> Tuple[bool, int]:
    """Return (ok, score). Score is simple heuristic 0..100."""
    score = 100
    # temperature
    if day['temp_high_c'] < prefs.get('min_temp_c', -100):
        score -= int((prefs['min_temp_c'] - day['temp_high_c']) * 3)
    # precip
    if day.get('precip', 0) > prefs.get('max_precip', 100):
        score -= int((day['precip'] - prefs['max_precip']) * 2)
    # wind
    if day.get('wind_kmh', 0) > prefs.get('max_wind_kmh', 999):
        score -= int((day['wind_kmh'] - prefs['max_wind_kmh']))
    # sun need
    if prefs.get('need_sun'):
        if not _desc_sunny(day.get('condition_code')):
            score -= 25
    # kite special: min wind
    if 'min_wind_kmh' in prefs:
        if day.get('wind_kmh', 0) < prefs['min_wind_kmh']:
            score -= int((prefs['min_wind_kmh'] - day.get('wind_kmh', 0)))
    return (score >= 75, max(0, score))