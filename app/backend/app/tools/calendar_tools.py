from datetime import datetime
from app.utils.prop_calendar_manager import PropCalendarManager
from langchain_core.tools import tool
from loguru import logger


# Global calendar manager
_calendar_manager = None

def get_calendar_manager():
    global _calendar_manager
    if _calendar_manager is None:
        _calendar_manager = PropCalendarManager()
    return _calendar_manager


@tool
def add_calendar_event(
    title: str,
    date: str,
    start_time: str = None,
    duration_hours: float = 2.0,
    location: str = None,
    description: str = None
) -> str:
    """
    Add an event to Google Calendar.
    
    Args:
        title: Event title
        date: Date in YYYY-MM-DD format (e.g., "2024-12-25")
        start_time: Start time in HH:MM format (e.g., "14:30") - optional for all-day events
        duration_hours: Duration in hours (default: 2.0)
        location: Event location (optional)
        description: Event description (optional)
    
    Returns:
        Success message with event details
    """
    try:
        manager = get_calendar_manager()
        event = manager.create_event(title, date, start_time, duration_hours, location, description)
        
        # Format display
        if 'dateTime' in event['start']:
            dt = datetime.fromisoformat(event['start']['dateTime'])
            time_str = f" at {dt.strftime('%H:%M')}"
        else:
            time_str = " (all-day)"
        
        result = f"✅ Event created: {event['title']}\n"
        result += f"📅 {date}{time_str}\n"
        if event['location']:
            result += f"📍 {event['location']}\n"
        result += f"🔗 {event['link']}\n"
        result += f"ID: {event['id']}"
        
        return result
        
    except Exception as e:
        return f"❌ Error creating event: {str(e)}"


@tool
def delete_calendar_event(event_identifier: str) -> str:
    """
    Delete a calendar event by ID or search term.
    
    Args:
        event_identifier: Event ID or search term (title, location, etc.)
        
    Returns:
        Success/failure message or confirmation request
    """
    try:
        manager = get_calendar_manager()
        
        # First, try to delete directly (assume it's an event ID)
        try:
            success = manager.delete_event(event_identifier)
            if success:
                return f"✅ Event deleted successfully"
        except:
            # Not a valid event ID, search for matching events
            pass
        
        # Search for matching events
        events = manager.search_events(event_identifier, max_results=10)
        
        if not events:
            return f"❌ No events found matching '{event_identifier}'"
        
        if len(events) == 1:
            # Only one match, delete it directly
            event = events[0]
            success = manager.delete_event(event['id'])
            if success:
                # Format display
                if 'dateTime' in event['start']:
                    dt = datetime.fromisoformat(event['start']['dateTime'])
                    time_str = dt.strftime('%Y-%m-%d at %H:%M')
                else:
                    time_str = f"{event['start']['date']} (all-day)"
                
                return f"✅ Deleted: {event['title']} on {time_str}"
            else:
                return f"❌ Failed to delete event"
        
        # Multiple matches - ask user to confirm
        result = f"🔍 Found {len(events)} events matching '{event_identifier}'. Please specify which one to delete:\n\n"
        
        for i, event in enumerate(events, 1):
            # Format start time
            if 'dateTime' in event['start']:
                dt = datetime.fromisoformat(event['start']['dateTime'])
                time_str = dt.strftime('%Y-%m-%d at %H:%M')
            else:
                time_str = f"{event['start']['date']} (all-day)"
            
            result += f"{i}. {event['title']}\n"
            result += f"   🗓️ {time_str}\n"
            if event['location']:
                result += f"   📍 {event['location']}\n"
            result += f"   🆔 To delete this event, use ID: {event['id']}\n\n"
        
        return result
        
    except Exception as e:
        return f"❌ Error deleting event: {str(e)}"


@tool
def update_calendar_event(
    event_identifier: str,
    title: str = None,
    date: str = None,
    start_time: str = None,
    duration_hours: float = None,
    location: str = None,
    description: str = None
) -> str:
    """
    Update an existing calendar event by ID or search term.
    
    Args:
        event_identifier: Event ID or search term (title, location, etc.)
        title: New title (optional)
        date: New date in YYYY-MM-DD format (optional)
        start_time: New start time in HH:MM format (optional)
        duration_hours: New duration in hours (optional)
        location: New location (optional)
        description: New description (optional)
        
    Returns:
        Success message with updated details or confirmation request
    """
    try:
        manager = get_calendar_manager()
        
        # First, try to update directly (assume it's an event ID)
        try:
            event = manager.update_event(event_identifier, title, date, start_time, duration_hours, location, description)
            
            # Format display
            if 'dateTime' in event['start']:
                dt = datetime.fromisoformat(event['start']['dateTime'])
                date_str = dt.strftime('%Y-%m-%d')
                time_str = f" at {dt.strftime('%H:%M')}"
            else:
                date_str = event['start']['date']
                time_str = " (all-day)"
            
            result = f"✅ Event updated: {event['title']}\n"
            result += f"📅 {date_str}{time_str}\n"
            if event['location']:
                result += f"📍 {event['location']}\n"
            result += f"🔗 {event['link']}\n"
            result += f"ID: {event['id']}"
            
            return result
            
        except:
            # Not a valid event ID, search for matching events
            pass
        
        # Search for matching events
        events = manager.search_events(event_identifier, max_results=10)
        
        if not events:
            return f"❌ No events found matching '{event_identifier}'"
        
        if len(events) == 1:
            # Only one match, update it directly
            event_to_update = events[0]
            event = manager.update_event(event_to_update['id'], title, date, start_time, duration_hours, location, description)
            
            # Format display
            if 'dateTime' in event['start']:
                dt = datetime.fromisoformat(event['start']['dateTime'])
                date_str = dt.strftime('%Y-%m-%d')
                time_str = f" at {dt.strftime('%H:%M')}"
            else:
                date_str = event['start']['date']
                time_str = " (all-day)"
            
            result = f"✅ Event updated: {event['title']}\n"
            result += f"📅 {date_str}{time_str}\n"
            if event['location']:
                result += f"📍 {event['location']}\n"
            result += f"🔗 {event['link']}\n"
            result += f"ID: {event['id']}"
            
            return result
        
        # Multiple matches - ask user to confirm
        result = f"🔍 Found {len(events)} events matching '{event_identifier}'. Please specify which one to update:\n\n"
        
        for i, event in enumerate(events, 1):
            # Format start time
            if 'dateTime' in event['start']:
                dt = datetime.fromisoformat(event['start']['dateTime'])
                time_str = dt.strftime('%Y-%m-%d at %H:%M')
            else:
                time_str = f"{event['start']['date']} (all-day)"
            
            result += f"{i}. {event['title']}\n"
            result += f"   🗓️ {time_str}\n"
            if event['location']:
                result += f"   📍 {event['location']}\n"
            result += f"   🆔 To update this event, use ID: {event['id']}\n\n"
        
        return result
        
    except Exception as e:
        return f"❌ Error updating event: {str(e)}"


@tool
def get_calendar_events(
    start_date: str,
    end_date: str,
    max_results: int = 50
) -> str:
    """
    Get calendar events within a date range.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        max_results: Maximum number of events to return (default: 50)
        
    Returns:
        List of events in the date range
    """
    try:
        manager = get_calendar_manager()
        events = manager.get_events(start_date, end_date, max_results)
        
        if not events:
            return f"📅 No events found from {start_date} to {end_date}"
        
        result = f"📅 {len(events)} event(s) from {start_date} to {end_date}:\n\n"
        
        for i, event in enumerate(events, 1):
            # Format start time
            if 'dateTime' in event['start']:
                dt = datetime.fromisoformat(event['start']['dateTime'])
                time_str = dt.strftime('%Y-%m-%d at %H:%M')
            else:
                time_str = f"{event['start']['date']} (all-day)"
            
            result += f"{i}. {event['title']}\n"
            result += f"   🗓️ {time_str}\n"
            if event['location']:
                result += f"   📍 {event['location']}\n"
            result += f"   ID: {event['id']}\n\n"
        
        return result
        
    except Exception as e:
        return f"❌ Error getting events: {str(e)}"


@tool
def search_calendar_events(query: str, max_results: int = 20) -> str:
    """
    Search calendar events by title, location, or description.
    
    Args:
        query: Search query
        max_results: Maximum results to return (default: 20)
        
    Returns:
        List of matching events
    """
    try:
        manager = get_calendar_manager()
        events = manager.search_events(query, max_results)
        
        if not events:
            return f"🔍 No events found matching '{query}'"
        
        result = f"🔍 {len(events)} event(s) matching '{query}':\n\n"
        
        for i, event in enumerate(events, 1):
            # Format start time
            if 'dateTime' in event['start']:
                dt = datetime.fromisoformat(event['start']['dateTime'])
                time_str = dt.strftime('%Y-%m-%d at %H:%M')
            else:
                time_str = f"{event['start']['date']} (all-day)"
            
            result += f"{i}. {event['title']}\n"
            result += f"   🗓️ {time_str}\n"
            if event['location']:
                result += f"   📍 {event['location']}\n"
            result += f"   ID: {event['id']}\n\n"
        
        return result
        
    except Exception as e:
        return f"❌ Error searching events: {str(e)}"