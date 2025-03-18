import requests

def find_last_n_meetings(event_id, n):
    all_events = requests.get("https://api.openf1.org/v1/meetings").json()

    # Keep only events where testing is not in meeting_name
    all_events = [event for event in all_events if "testing" not in event["meeting_name"].lower()]

    # Get a unique list of meeting_keys ordered by date_start
    meeting_keys = sorted(list(set([event["meeting_key"] for event in all_events])))

    # Find the index of the given event_id
    try:
        event_index = meeting_keys.index(event_id)
    except ValueError:
        print(f'Event {event_id} not found')
        return []

    # Get all the last_events before the given event_id
    last_n_events = meeting_keys[:event_index]

    try:
        # Try to select the last n events
        last_n_events = last_n_events[-n:]
    except IndexError:
        # If there are less than n events, return all previous events
        last_n_events = last_n_events

    return last_n_events

if __name__ == "__main__":
    print(f'{find_last_n_meetings(1140, 3)}\n')
    print(f'{find_last_n_meetings(1141, 3)}\n')
    print(f'{find_last_n_meetings(1142, 3)}\n')
    print(f'{find_last_n_meetings(1143, 3)}\n')
    print(f'{find_last_n_meetings(1207, 3)}\n')
