import requests
from collections import defaultdict

def get_all_race_weekends():
    # Get session keys from OpenF1 API
    response = requests.get('https://api.openf1.org/v1/sessions')
    sessions = response.json()

    # Get a list of all meeting_keys that have a record where there is a session_type of 'Race'
    # (This removes pre-season testing)
    race_sessions = [session for session in sessions if session['session_type'] == 'Race']
    race_meeting_keys = [session['meeting_key'] for session in race_sessions]

    # Filter the sessions to remove any that have a meeting_key that is not in the race_meeting_keys list
    sessions = [session for session in sessions if session['meeting_key'] in race_meeting_keys]

    # Group sessions by meeting_key
    grouped_sessions = defaultdict(dict)
    session_order = ['Practice 1', 'Practice 2', 'Practice 3', 'Sprint Shootout', 'Sprint', 'Race']
    
    for session in sessions:
        meeting_key = session['meeting_key']
        session_type = session['session_name']
        
        if session_type in session_order:
            grouped_sessions[meeting_key][session_type] = session

    # Convert to ordered list of dictionaries
    ordered_weekends = []
    for meeting_key in sorted(grouped_sessions.keys()):
        first_session = next(s for s in grouped_sessions[meeting_key].values() if s is not None)
        weekend = {
            'meeting_key': meeting_key,
            'location': first_session['location'],
            'country_key': first_session['country_key'],
            'country_code': first_session['country_code'],
            'country_name': first_session['country_name'],
            'circuit_key': first_session['circuit_key'],
            'circuit_short_name': first_session['circuit_short_name'],
            'year': first_session['year'],
            'sessions': [
                {
                    'session_type': grouped_sessions[meeting_key].get(session_type, {}).get('session_type'),
                    'session_name': session_type,
                    'date_start': grouped_sessions[meeting_key].get(session_type, {}).get('date_start'),
                    'date_end': grouped_sessions[meeting_key].get(session_type, {}).get('date_end'),
                    'gmt_offset': grouped_sessions[meeting_key].get(session_type, {}).get('gmt_offset'),
                    'session_key': grouped_sessions[meeting_key].get(session_type, {}).get('session_key')
                } if grouped_sessions[meeting_key].get(session_type) else None
                for session_type in session_order
            ]
        }
        ordered_weekends.append(weekend)

    return ordered_weekends

if __name__ == '__main__':
    print(get_all_race_weekends())
