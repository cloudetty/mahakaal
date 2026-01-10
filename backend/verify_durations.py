import sys
import os
import datetime

# Add the backend directory to the path so we can import skills_google
sys.path.append(os.path.join(os.getcwd(), "backend"))

from skills_google import schedule_event, update_event, search_events, delete_event

def verify():
    print("--- Verifying Granular Durations ---")
    
    # 1. Schedule a 15-minute event
    date_str = (datetime.datetime.now() + datetime.timedelta(days=2)).strftime("%Y-%m-%d")
    time_str = "10:00"
    title = "Quick 15-min Sync"
    
    print(f"Scheduling '{title}' for 15 minutes...")
    result = schedule_event(title, date_str, time_str, duration_minutes=15)
    print(f"Result: {result}")
    
    # 2. Search for it and verify
    print("\nSearching for the event...")
    search_result = search_events(title)
    print(f"Search Result:\n{search_result}")
    
    if "[" in search_result and "]" in search_result:
        event_id = search_result.split("[")[1].split("]")[0]
        print(f"Found Event ID: {event_id}")
        
        # 3. Update to 45 minutes
        print(f"\nUpdating event {event_id} to 45 minutes...")
        update_result = update_event(event_id, duration_minutes=45)
        print(f"Update Result: {update_result}")
        
        # 4. Clean up
        # print(f"\nDeleting test event...")
        # delete_result = delete_event(event_id)
        # print(f"Delete Result: {delete_result}")
    else:
        print("Could not find event to update.")

if __name__ == "__main__":
    verify()
