from typing import List, Dict
from app.utils.utils import _desc_sunny, _meets_prefs
from app.utils.constants import _ACTIVITY_PREFS
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from app.tools.weather_scraper import get_weather_data

llm_flash = ChatGoogleGenerativeAI(model="gemini-2.5-flash")



async def _get_place_recommendations_with_timing(
    activity: str, 
    timeframe_days: int = 7, 
    near_city: str = None, 
    k: int = 5
) -> str:
    """
    Core function to recommend places for an activity with specific day suggestions within a timeframe.
    This is the shared implementation used by multiple tools.
    """
    # Validate inputs
    timeframe_days = max(1, min(10, int(timeframe_days)))
    activity_lower = activity.lower()
    prefs = _ACTIVITY_PREFS.get(activity_lower)
    
    if not prefs:
        return f"Unknown activity '{activity}'. Available activities: {', '.join(_ACTIVITY_PREFS.keys())}"

    # Generate candidate locations
    if near_city:
        prompt = (
            f"Suggest {k * 2} specific towns, parks, or locations ideal for '{activity}' "
            f"within 500km of {near_city}. Include variety of distances. "
            f"Return only the names, comma-separated, no descriptions."
        )
    else:
        prompt = (
            f"Suggest {k * 2} cities worldwide that are famous for '{activity}'. "
            f"Include variety from different continents and climates. "
            f"Return only city names, comma-separated, no descriptions."
        )

    try:
        resp = await llm_flash.ainvoke(prompt)
        text = (getattr(resp, 'content', None) or '').strip()
        candidates = [c.strip() for c in text.split(',') if c.strip()]
    except Exception as e:
        return f"Error generating location suggestions: {str(e)}"

    # Analyze weather for each candidate
    place_recommendations: List[Dict] = []
    
    for city in candidates[:k * 2]:  # Check more than we need
        try:
            weather_data = get_weather_data(city)
            
            if "error" in weather_data:
                continue
                
            forecast = weather_data.get('forecast', [])[:timeframe_days]
            if not forecast:
                continue
            
            # Find best days for this activity at this location
            good_days = []
            for day in forecast:
                is_suitable, score = _meets_prefs(day, prefs)
                if is_suitable:
                    good_days.append({
                        'day': day.get('day', 'Unknown'),
                        'date': day.get('date', 'Unknown'),
                        'score': score,
                        'condition': day.get('condition', ''),
                        'temp_high': day.get('temp_high_c', 0),
                        'temp_low': day.get('temp_low_c', 0),
                        'precip': day.get('precip', 0),
                        'wind': day.get('wind_kmh', 0)
                    })
            
            if good_days:
                # Sort by score (best first)
                good_days.sort(key=lambda x: x['score'], reverse=True)
                
                place_recommendations.append({
                    'city': weather_data['city'],
                    'good_days': good_days,
                    'best_score': good_days[0]['score'],
                    'num_good_days': len(good_days)
                })
                
        except Exception as e:
            continue  # Skip problematic locations
    
    # Sort places by best score, then by number of good days
    place_recommendations.sort(key=lambda x: (x['best_score'], x['num_good_days']), reverse=True)
    
    if not place_recommendations:
        return f"No suitable places found for {activity} in the next {timeframe_days} days. Weather conditions may not be favorable."
    
    # Format results
    result_lines = [
        f"🎯 Best places for {activity} in the next {timeframe_days} days:\n"
    ]
    
    for i, place in enumerate(place_recommendations[:k], 1):
        city = place['city']
        good_days = place['good_days']
        
        result_lines.append(f"{i}. **{city}** ({len(good_days)} good day{'s' if len(good_days) != 1 else ''})")
        
        # Show top 3 days or all if fewer
        days_to_show = good_days[:min(3, len(good_days))]
        for day in days_to_show:
            result_lines.append(
                f"   • {day['date']} ({day['day']}): {day['condition']} - "
                f"{day['temp_high']:.0f}°C/{day['temp_low']:.0f}°C, "
                f"Rain: {day['precip']}%, Wind: {day['wind']:.0f}km/h "
                f"(Score: {day['score']}/100)"
            )
        
        if len(good_days) > 3:
            result_lines.append(f"   ... and {len(good_days) - 3} more good day{'s' if len(good_days) - 3 != 1 else ''}")
        
        result_lines.append("")  # Empty line between places
    
    return "\n".join(result_lines)

@tool
async def recommend_places_tool(activity: str, near_city: str = None, k: int = 6) -> str:
    """Suggest up to k places for an activity; filters by current weather."""
    prefs = _ACTIVITY_PREFS.get(activity.lower())
    if not prefs:
        return f"Unknown activity '{activity}'."

    if near_city:
        prompt = (
            f"Suggest {k} specific towns, parks, or locations ideal for '{activity}' near {near_city}. "
            f"Return only the names, comma-separated."
        )
    else:
        prompt = (
            f"Suggest {k} cities worldwide that are famous for '{activity}'. "
            f"Return only city names, comma-separated."
        )

    resp = await llm_flash.ainvoke(prompt)
    text = (getattr(resp, 'content', None) or '').strip()
    candidates = [c.strip() for c in text.split(',') if c.strip()]

    accepted: List[str] = []
    for city in candidates:
        try:
            d = get_weather_data(city)
            cur = d['current']
            # basic filter using prefs
            ok_temp = cur['temperature_c'] >= prefs['min_temp_c']
            ok_sun = True if not prefs.get('need_sun') else _desc_sunny(cur['condition_code'])
            ok = ok_temp and ok_sun
            if ok:
                accepted.append(f"{city}: {cur['temperature_c']:.1f}°C, {cur['condition']}, humidity {cur['humidity']}%, wind {cur['wind_kmh']:.0f} km/h")
        except Exception:
            continue

    if not accepted:
        return f"No good matches right now for {activity}."

    return "Good cities right now for {act}:\n".replace('{act}', activity) + "\n".join(accepted[:k])


@tool
async def recommend_places_with_timing_tool(
    activity: str, 
    days: int = 7, 
    near_city: str = None, 
    k: int = 5
) -> str:
    """
    Recommend places for an activity with specific day suggestions within a timeframe.
    
    Args:
        activity: The activity to search for (e.g., 'hiking', 'beach', 'skiing')
        days: Number of days to look ahead (1-10)
        near_city: Optional city to search near
        k: Maximum number of places to recommend
    
    Returns:
        Formatted string with places and their best days for the activity
    """
    return await _get_place_recommendations_with_timing(activity, days, near_city, k)


@tool
async def where_can_i_go_tool(
    activity: str, 
    days: int = 7,
    near_city: str = None,
    k: int = 3
) -> str:
    """
    Answer questions like 'where can I go skiing next week' or 'where can I go hiking in 3 days'.
    
    Args:
        activity: The activity you want to do
        days: Number of days to look ahead (1-10). Agent should parse natural language timeframes.
        near_city: Optional city to search near
        k: Number of recommendations
    
    Returns:
        Personalized recommendations with timing
    """
    # Use the shared implementation
    result = await _get_place_recommendations_with_timing(
        activity=activity,
        timeframe_days=days,
        near_city=near_city,
        k=k
    )
    
    # Add personalized intro based on days
    location_phrase = f" near {near_city}" if near_city else ""
    
    # timeframe description from days
    if days == 0:
        timeframe_desc = "today"
    elif days == 1:
        timeframe_desc = "tomorrow"
    elif 2 <= days <= 6:
        timeframe_desc = "next 5 days"
    elif days == 7:
        timeframe_desc = "next week"
    else:
        timeframe_desc = f"next {days} days"
    
    intro = f"Here's where you can go for {activity}{location_phrase} in the {timeframe_desc}:\n\n"
    
    return intro + result


@tool
def get_activity_weather_summary_tool(city: str, activity: str, days: int = 7) -> str:
    """
    Get detailed weather analysis for a specific activity at a specific location.
    
    Args:
        city: City to check
        activity: Activity to analyze for
        days: Number of days to analyze (1-10)
    
    Returns:
        Detailed day-by-day suitability analysis
    """
    days = max(1, min(10, int(days)))
    activity_lower = activity.lower()
    prefs = _ACTIVITY_PREFS.get(activity_lower)
    
    if not prefs:
        return f"Unknown activity '{activity}'. Available: {', '.join(_ACTIVITY_PREFS.keys())}"
    
    try:
        weather_data = get_weather_data(city)
        
        if "error" in weather_data:
            return f"Could not get weather data for {city}"
        
        forecast = weather_data.get('forecast', [])[:days]
        if not forecast:
            return f"No forecast data available for {city}"
        
        result_lines = [
            f"🌤️ {activity.title()} weather analysis for {weather_data['city']} ({days} days):\n"
        ]
        
        for day in forecast:
            is_suitable, score = _meets_prefs(day, prefs)
            
            # Determine suitability level
            if score >= 90:
                suitability = "🌟 Excellent"
            elif score >= 80:
                suitability = "✅ Very Good"
            elif score >= 70:
                suitability = "👍 Good"
            elif score >= 60:
                suitability = "⚠️ Fair"
            else:
                suitability = "❌ Poor"
            
            result_lines.append(
                f"{day.get('date', 'Unknown')} ({day.get('day', 'Unknown')}): {suitability} ({score}/100)\n"
                f"  Weather: {day.get('condition', 'Unknown')} - "
                f"H: {day.get('temp_high_c', 0):.0f}°C, L: {day.get('temp_low_c', 0):.0f}°C\n"
                f"  Rain: {day.get('precip', 0)}%, Wind: {day.get('wind_kmh', 0):.0f}km/h\n"
            )
        
        # Add activity-specific tips
        tips = []
        if prefs.get('min_temp_c'):
            tips.append(f"Minimum comfortable temperature: {prefs['min_temp_c']}°C")
        if prefs.get('max_precip'):
            tips.append(f"Avoid if rain chance > {prefs['max_precip']}%")
        if prefs.get('need_sun'):
            tips.append("Sunny conditions preferred")
        if prefs.get('min_wind_kmh'):
            tips.append(f"Minimum wind needed: {prefs['min_wind_kmh']}km/h")
        
        if tips:
            result_lines.append(f"💡 {activity.title()} requirements: {', '.join(tips)}")
        
        return "\n".join(result_lines)
        
    except Exception as e:
        return f"Error analyzing weather for {activity} in {city}: {str(e)}"