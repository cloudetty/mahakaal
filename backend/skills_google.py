import os.path
import datetime
import json
from typing import List, Dict, Any, Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]

CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"

def _get_calendar_service():
    """Shows basic usage of the Google Calendar API."""
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(f"Missing {CREDENTIALS_FILE}. Please add it to the backend folder.")
            
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    service = build("calendar", "v3", credentials=creds)
    return service

def get_current_datetime() -> str:
    """Returns the current date and time with day of the week in a human-readable format."""
    return datetime.datetime.now().strftime("%A, %Y-%m-%d %H:%M:%S")

def list_events(date_str: str) -> str:
    """
    Checks if there are any events on the given date (YYYY-MM-DD).
    Returns a list of events or a message saying it's clear.
    """
    try:
        service = _get_calendar_service()
        
        # Parse date range for the entire day logic using local time
        # Get local timezone
        local_tz = datetime.datetime.now().astimezone().tzinfo
        
        # Create aware datetimes for start and end of day
        dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        start_of_day = dt.replace(hour=0, minute=0, second=0, tzinfo=local_tz).isoformat()
        end_of_day = dt.replace(hour=23, minute=59, second=59, tzinfo=local_tz).isoformat()

        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=start_of_day,
                timeMax=end_of_day,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            return f"No events found for {date_str}. You are free."

        response = f"Events on {date_str}:\n"
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            summary = event.get("summary", "No Title")
            # Formatting start time slightly for readability
            response += f"- [{event['id']}] {start}: {summary}\n"
            
        return response

    except HttpError as error:
        return f"An error occurred: {error}"
    except Exception as e:
        return f"System Error: {str(e)}"

def list_events_range(start_date: str, days: int = 7) -> str:
    """
    Lists events for a range of days starting from start_date.
    """
    try:
        service = _get_calendar_service()
        local_tz = datetime.datetime.now().astimezone().tzinfo
        
        dt_start = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        time_min = dt_start.replace(hour=0, minute=0, second=0, tzinfo=local_tz).isoformat()
        
        dt_end = dt_start + datetime.timedelta(days=days)
        time_max = dt_end.replace(hour=23, minute=59, second=59, tzinfo=local_tz).isoformat()

        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            return f"No events found from {start_date} to {(dt_start + datetime.timedelta(days=days-1)).strftime('%Y-%m-%d')}."

        response = f"Events from {start_date} for {days} days:\n"
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            summary = event.get("summary", "No Title")
            response += f"- [{event['id']}] {start}: {summary}\n"
            
        return response

    except HttpError as error:
        return f"An error occurred: {error}"
    except Exception as e:
        return f"System Error: {str(e)}"

def search_events(query: str, days_range: int = 30) -> str:
    """
    Search for events by title/summary over a range of days from today.
    """
    try:
        service = _get_calendar_service()
        local_tz = datetime.datetime.now().astimezone().tzinfo
        
        now = datetime.datetime.now(local_tz)
        time_min = now.isoformat()
        
        future = now + datetime.timedelta(days=days_range)
        time_max = future.isoformat()

        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=time_min,
                timeMax=time_max,
                q=query,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            return f"No events found matching '{query}' in the next {days_range} days."

        response = f"Search results for '{query}' (next {days_range} days):\n"
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            summary = event.get("summary", "No Title")
            response += f"- [{event['id']}] {start}: {summary}\n"
            
        return response

    except HttpError as error:
        return f"An error occurred: {error}"
    except Exception as e:
        return f"System Error: {str(e)}"

def schedule_event(title: str, date_str: str, time_str: str, duration_minutes: int = 60, attendees: Optional[List[str]] = None) -> str:
    """
    Schedules an event.
    date_str: YYYY-MM-DD
    time_str: HH:MM
    duration_minutes: Duration in minutes (default 60)
    attendees: List of email strings
    """
    try:
        service = _get_calendar_service()
        
        # Combine date and time
        # Get local timezone dynamically
        local_tz = datetime.datetime.now().astimezone().tzinfo
        
        # Better approach: Use fully aware datetimes for start/end
        start_dt = datetime.datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M").replace(tzinfo=local_tz)
        end_dt = start_dt + datetime.timedelta(minutes=duration_minutes)
        
        event = {
            "summary": title,
            "start": {
                "dateTime": start_dt.isoformat(),
            },
            "end": {
                "dateTime": end_dt.isoformat(),
            },
        }

        if attendees:
            event["attendees"] = [{"email": email} for email in attendees]

        created_event = service.events().insert(calendarId="primary", body=event).execute()
        
        return f"Confirmed. Event created: {created_event.get('htmlLink')}"

    except HttpError as error:
        return f"An error occurred: {error}"
    except Exception as e:
        return f"System Error: {str(e)}"

def update_event(event_id: str, title: Optional[str] = None, date_str: Optional[str] = None, time_str: Optional[str] = None, duration_minutes: Optional[int] = None, attendees: Optional[List[str]] = None) -> str:
    """
    Updates an existing event's details.
    """
    try:
        service = _get_calendar_service()
        
        # Get existing event first to patch it
        event = service.events().get(calendarId="primary", eventId=event_id).execute()
        
        if title:
            event["summary"] = title
            
        if date_str or time_str or duration_minutes:
            # We need to reconstruct the start/end if either changes
            # Get current start as anchor if one is missing
            current_start = event["start"].get("dateTime", event["start"].get("date"))
            dt_start = datetime.datetime.fromisoformat(current_start.replace('Z', '+00:00'))
            
            # Use current end to calculate duration if duration_minutes is not provided
            current_end = event["end"].get("dateTime", event["end"].get("date"))
            dt_end = datetime.datetime.fromisoformat(current_end.replace('Z', '+00:00'))
            current_duration = int((dt_end - dt_start).total_seconds() / 60)
            
            new_date = date_str if date_str else dt_start.strftime("%Y-%m-%d")
            new_time = time_str if time_str else dt_start.strftime("%H:%M")
            new_duration = duration_minutes if duration_minutes is not None else current_duration
            
            local_tz = datetime.datetime.now().astimezone().tzinfo
            final_start_dt = datetime.datetime.strptime(f"{new_date} {new_time}", "%Y-%m-%d %H:%M").replace(tzinfo=local_tz)
            final_end_dt = final_start_dt + datetime.timedelta(minutes=new_duration)
            
            event["start"] = {"dateTime": final_start_dt.isoformat()}
            event["end"] = {"dateTime": final_end_dt.isoformat()}
            
        if attendees:
            # Replace existing list
            event["attendees"] = [{"email": email} for email in attendees]

        updated_event = service.events().update(calendarId="primary", eventId=event_id, body=event).execute()
        return f"Event updated successfully: {updated_event.get('htmlLink')}"

    except HttpError as error:
        return f"An error occurred: {error}"
    except Exception as e:
        return f"System Error: {str(e)}"

def delete_event(event_id: str) -> str:
    """
    Deletes an event by its ID.
    """
    try:
        service = _get_calendar_service()
        service.events().delete(calendarId="primary", eventId=event_id).execute()
        return "Event deleted successfully."
    except HttpError as error:
        return f"An error occurred: {error}"
    except Exception as e:
        return f"System Error: {str(e)}"


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
            "name": "list_events",
            "description": "List events from the Google Calendar for a specific date. Use this to get the daily agenda or check availability.",
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
            "description": "Schedule a new event on the Google Calendar. Default duration is 60 minutes if not specified.",
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
                    },
                    "duration_minutes": {
                        "type": "integer",
                        "description": "The duration of the event in minutes (default is 60)."
                    },
                    "attendees": {
                        "type": "array",
                        "items": { "type": "string" },
                        "description": "A list of email addresses to invite as attendees."
                    }
                },
                "required": ["title", "date_str", "time_str"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_event",
            "description": "Update an existing event. Use this to change the title, time, duration, or add attendees/invitations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "event_id": {
                        "type": "string",
                        "description": "The unique identifier of the event to update."
                    },
                    "title": {
                        "type": "string",
                        "description": "New title for the event (optional)."
                    },
                    "date_str": {
                        "type": "string",
                        "description": "New date in YYYY-MM-DD format (optional)."
                    },
                    "time_str": {
                        "type": "string",
                        "description": "New time in HH:MM format (optional)."
                    },
                    "duration_minutes": {
                        "type": "integer",
                        "description": "New duration in minutes (optional)."
                    },
                    "attendees": {
                        "type": "array",
                        "items": { "type": "string" },
                        "description": "New list of email addresses to invite (replaces existing list)."
                    }
                },
                "required": ["event_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_event",
            "description": "Delete an event from the calendar. You MUST get the event ID from 'list_events' or 'search_events' first.",
            "parameters": {
                "type": "object",
                "properties": {
                    "event_id": {
                        "type": "string",
                        "description": "The unique identifier of the event to delete."
                    }
                },
                "required": ["event_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_events_range",
            "description": "List events over a range of days. Useful for looking at the week ahead or finding events on specific upcoming days.",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "The start date in YYYY-MM-DD format."
                    },
                    "days": {
                        "type": "integer",
                        "description": "The number of days to include in the range (default is 7)."
                    }
                },
                "required": ["start_date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_events",
            "description": "Search for events by title or keyword. Use this to find specific appointments when the exact date is unknown.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search term (e.g., 'Gym', 'Doctor')."
                    },
                    "days_range": {
                        "type": "integer",
                        "description": "How many days into the future to search (default is 30)."
                    }
                },
                "required": ["query"]
            }
        }
    }
]

def execute_tool_call(tool_name: str, arguments: Dict[str, Any]) -> str:
    if tool_name == "get_current_datetime":
        return get_current_datetime()
    elif tool_name == "list_events":
        return list_events(arguments.get("date_str"))
    elif tool_name == "schedule_event":
        return schedule_event(
            arguments.get("title"), 
            arguments.get("date_str"), 
            arguments.get("time_str"),
            arguments.get("duration_minutes", 60),
            arguments.get("attendees")
        )
    elif tool_name == "update_event":
        return update_event(
            arguments.get("event_id"),
            arguments.get("title"),
            arguments.get("date_str"),
            arguments.get("time_str"),
            arguments.get("duration_minutes"),
            arguments.get("attendees")
        )
    elif tool_name == "delete_event":
        return delete_event(arguments.get("event_id"))
    elif tool_name == "list_events_range":
        return list_events_range(
            arguments.get("start_date"),
            arguments.get("days", 7)
        )
    elif tool_name == "search_events":
        return search_events(
            arguments.get("query"),
            arguments.get("days_range", 30)
        )
    else:
        return f"Error: Unknown tool '{tool_name}'"
