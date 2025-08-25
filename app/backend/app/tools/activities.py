from typing import List
from app.utils.utils import _meets_prefs
from langchain_core.tools import tool
from app.utils.constants import _ACTIVITY_PREFS
from app.tools.weather_scraper import get_weather_data
from loguru import logger


@tool
def find_best_weather_day_tool(city: str, activity: str = "outdoor") -> str:
    """Find the best day (next 7) for an activity using _ACTIVITY_PREFS."""
    prefs = _ACTIVITY_PREFS.get(activity.lower())
    if not prefs:
        return f"Unknown activity '{activity}'."
    data = get_weather_data(city)
    best = None
    best_score = -1
    for d in data['forecast'][:7]:
        ok, sc = _meets_prefs(d, prefs)
        if sc > best_score:
            best_score, best = sc, d
    if not best:
        return f"No good day found for {activity} in {city}."
    return (
        f"Best day for {activity} in {city}: {best['date']} — {best['condition']}\n"
        f"Temp H {best['temp_high_c']:.0f}°C / L {best['temp_low_c']:.0f}°C, Rain {best['precip']}%, Score {best_score}/100"
    )


@tool
def suggest_activities_tool(cities: List[str], days: int = 3) -> str:
    """Suggest top activities for one or more cities over next N days (1..7)."""
    days = max(1, min(7, int(days)))
    lines: List[str] = []
    for city in cities[:5]:
        data = get_weather_data(city)
        lines.append(f"Activity suggestions for {data['city']} (next {days} days):")
        for d in data['forecast'][:days]:
            picks: List[str] = []
            scored = []
            for act, prefs in _ACTIVITY_PREFS.items():
                ok, sc = _meets_prefs(d, prefs)
                if ok:
                    scored.append((sc, act))
            scored.sort(reverse=True)
            if not scored:
                alt = 'Consider indoor plans (museums, cinema, gym).'
                lines.append(f"- {d['date']} {d['condition']} {d['temp_high_c']:.0f}°C: {alt}")
            else:
                top = ', '.join([f"{act} (score {sc})" for sc, act in scored[:3]])
                lines.append(f"- {d['date']} {d['condition']} {d['temp_high_c']:.0f}°C: {top}")
    return "\n".join(lines)