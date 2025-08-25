import uuid
from datetime import datetime, timedelta, date

class PropCalendarManager:
    """Prop in-memory Google Calendar replacement for testing."""

    def __init__(self):
        self.events = {}

    def _parse_datetime(self, date_str: str, time_str: str = None):
        """Return event start format compatible with Google Calendar."""
        if time_str:
            dt = datetime.fromisoformat(f"{date_str}T{time_str}")
            return {"dateTime": dt.isoformat(), "timeZone": "UTC"}
        else:
            return {"date": date_str}

    def create_event(self, title, date, start_time=None,
                     duration_hours=2.0, location=None, description=None):
        event_id = str(uuid.uuid4())
        start_dt = self._parse_datetime(date, start_time)

        if "dateTime" in start_dt:
            start_datetime = datetime.fromisoformat(start_dt["dateTime"])
            end_datetime = start_datetime + timedelta(hours=duration_hours)
            end_dt = {"dateTime": end_datetime.isoformat(), "timeZone": "UTC"}
        else:
            # all-day events just reuse the same date
            end_dt = {"date": date}

        event = {
            "id": event_id,
            "title": title,
            "start": start_dt,
            "end": end_dt,
            "location": location or "",
            "description": description or "",
            "link": f"http://Prop.calendar/{event_id}"
        }
        self.events[event_id] = event
        return event

    def delete_event(self, event_id: str) -> bool:
        return self.events.pop(event_id, None) is not None

    def update_event(self, event_id, title=None, date=None, start_time=None,
                     duration_hours=None, location=None, description=None):
        if event_id not in self.events:
            raise ValueError("Event not found")

        event = self.events[event_id]

        if title:
            event["title"] = title

        if date or start_time or duration_hours:
            old_start = event["start"]

            # current values
            current_date = old_start.get("date") or datetime.fromisoformat(
                old_start["dateTime"]).strftime("%Y-%m-%d")
            current_time = None
            if "dateTime" in old_start:
                current_time = datetime.fromisoformat(
                    old_start["dateTime"]).strftime("%H:%M")

            # new values
            new_date = date or current_date
            new_time = start_time or current_time
            start_dt = self._parse_datetime(new_date, new_time)
            event["start"] = start_dt

            if "dateTime" in start_dt:
                start_datetime = datetime.fromisoformat(start_dt["dateTime"])
                hours = duration_hours if duration_hours else (
                    (datetime.fromisoformat(event["end"]["dateTime"]) - start_datetime).seconds / 3600
                    if "dateTime" in event["end"] else 2.0
                )
                event["end"] = {
                    "dateTime": (start_datetime + timedelta(hours=hours)).isoformat(),
                    "timeZone": "UTC"
                }
            else:
                event["end"] = {"date": new_date}

        if location is not None:
            event["location"] = location
        if description is not None:
            event["description"] = description

        self.events[event_id] = event
        return event

    def get_events(self, start_date, end_date, max_results=50):
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        results = []
        for e in self.events.values():
            if "dateTime" in e["start"]:
                dt = datetime.fromisoformat(e["start"]["dateTime"])
                if start <= dt <= end:
                    results.append(e)
            else:
                d = date.fromisoformat(e["start"]["date"])
                if start.date() <= d <= end.date():
                    results.append(e)
        return results[:max_results]

    def search_events(self, query, max_results=20):
        query_lower = query.lower()
        results = []
        for e in self.events.values():
            if (query_lower in e["title"].lower() or
                query_lower in e.get("location", "").lower() or
                query_lower in e.get("description", "").lower()):
                results.append(e)
        return results[:max_results]
