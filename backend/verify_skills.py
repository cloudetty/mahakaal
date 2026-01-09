from skills_google import get_current_datetime, list_events_range, search_events
import datetime

def test():
    print("--- Testing get_current_datetime ---")
    print(get_current_datetime())
    
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    print("\n--- Testing list_events_range (3 days) ---")
    print(list_events_range(today, days=3))
    
    print("\n--- Testing search_events (Gym) ---")
    print(search_events("Gym"))

if __name__ == "__main__":
    test()
