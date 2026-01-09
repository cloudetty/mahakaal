import json
import datetime
from pathlib import Path
from typing import List, Dict, Any

EVENTS_FILE = Path(__file__).parent / "events.json"

def _load_events() -> List[Dict[str, Any]]:
    if not EVENTS_FILE.exists():
        return []
    try:
        with open(EVENTS_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def _save_events(events: List[Dict[str, Any]]):
    with open(EVENTS_FILE, "w") as f:
        json.dump(events, f, indent=2)

def get_current_datetime() -> str:
    """Returns the current date and time in a human-readable format."""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def check_availability(date_str: str) -> str:
    """
    Checks if there are any events on the given date (YYYY-MM-DD).
    Returns a list of events or a message saying it's clear.
    """
    events = _load_events()
    day_events = [e for e in events if e.get("date") == date_str]
    
    if not day_events:
        return f"No events scheduled for {date_str}. You are free."
    
    response = f"Events on {date_str}:\n"
    for event in day_events:
        response += f"- {event['time']}: {event['title']}\n"
    return response

def schedule_event(title: str, date_str: str, time_str: str) -> str:
    """
    Schedules an event.
    date_str: YYYY-MM-DD
    time_str: HH:MM
    """
    events = _load_events()
    
    # Simple conflict check (very basic for now)
    for event in events:
        if event.get("date") == date_str and event.get("time") == time_str:
            return f"Conflict! You already have '{event['title']}' at {time_str} on {date_str}."
    
    new_event = {
        "id": len(events) + 1,
        "title": title,
        "date": date_str,
        "time": time_str,
        "created_at": get_current_datetime()
    }
    
    events.append(new_event)
    _save_events(events)
    
    return f"Confirmed. '{title}' has been scheduled for {date_str} at {time_str}."

# Registry of available tools for the Agent to inspect
AVAILABLE_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_current_datetime",
            "description": "Get the current date and time. Use this when the user mentions relative times like 'tomorrow' or 'now'.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_availability",
            "description": "Check the calendar for events on a specific date.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date_str": {
                        "type": "string",
                        "description": "The date to check in YYYY-MM-DD format."
                    }
                },
                "required": ["date_str"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "schedule_event",
            "description": "Schedule a new event on the calendar.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The title or subject of the event."
                    },
                    "date_str": {
                        "type": "string",
                        "description": "The date of the event in YYYY-MM-DD format."
                    },
                    "time_str": {
                        "type": "string",
                        "description": "The time of the event in HH:MM format (24-hour)."
                    }
                },
                "required": ["title", "date_str", "time_str"]
            }
        }
    }
]

def execute_tool_call(tool_name: str, arguments: Dict[str, Any]) -> str:
    if tool_name == "get_current_datetime":
        return get_current_datetime()
    elif tool_name == "check_availability":
        return check_availability(arguments.get("date_str"))
    elif tool_name == "schedule_event":
        return schedule_event(
            arguments.get("title"), 
            arguments.get("date_str"), 
            arguments.get("time_str")
        )
    else:
        return f"Error: Unknown tool '{tool_name}'"
