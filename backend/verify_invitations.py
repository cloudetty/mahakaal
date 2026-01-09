from skills_google import schedule_event, update_event, list_events, delete_event, search_events
import datetime

def test_invitations():
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    print(f"--- Testing schedule_event with attendees (Date: {today}) ---")
    result = schedule_event(
        title="Workout with Buddy TEST",
        date_str=today,
        time_str="23:00",
        attendees=["abhijiths465@gmail.com"]
    )
    print(result)
    
    # Extract event ID from link if possible, or search for it
    print("\n--- Searching for the created event ---")
    search_res = search_events("Workout with Buddy TEST")
    print(search_res)
    
    # Try to find ID in search results
    import re
    ids = re.findall(r'\[(.*?)\]', search_res)
    if ids:
        event_id = ids[0]
        print(f"\n--- Testing update_event (Add another attendee) for ID: {event_id} ---")
        update_res = update_event(
            event_id=event_id,
            attendees=["abhijiths465@gmail.com", "test@example.com"]
        )
        print(update_res)
        
        print("\n--- Cleaning up (Deleting test event) ---")
        del_res = delete_event(event_id)
        print(del_res)
    else:
        print("Could not find event ID for testing update/delete.")

if __name__ == "__main__":
    test_invitations()
