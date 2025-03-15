import requests

def get_session_lap_data(session_key):
    """
    Gets lap data for a session

    Args:
        session_key (str): The key of the session to get lap data for

    Returns:
        list: A list of dictionaries containing lap data
    """
    laps = requests.get(f'https://api.openf1.org/v1/laps?session_key={session_key}')
    return laps.json()

def get_session_stint_data(session_key):
    """
    Gets stint data for a session

    Args:
        session_key (str): The key of the session to get stint data for

    Returns:
        list: A list of dictionaries containing stint data
    """
    stints = requests.get(f'https://api.openf1.org/v1/stints?session_key={session_key}')
    return stints.json()

def practice_session_combined_data(session_key):
    """
    Combines lap and stint data for a practice session

    Args:
        session_key (str): The key of the session to combine data for

    Returns:
        list: A list of dictionaries containing combined lap and stint data
    """
    laps = get_session_lap_data(session_key)
    stints = get_session_stint_data(session_key)
    
    # Create a lookup dictionary for stints
    stint_lookup = {}
    for stint in stints:
        driver = stint['driver_number']
        for lap_num in range(stint['lap_start'], stint['lap_end'] + 1):
            key = (driver, lap_num)
            stint_lookup[key] = {
                'compound': stint['compound'],
                'stint_number': stint['stint_number'],
                'tyre_age_at_start': stint['tyre_age_at_start']
            }
    
    # Combine lap data with stint information
    combined_data = []
    for lap in laps:
        key = (lap['driver_number'], lap['lap_number'])
        stint_info = stint_lookup.get(key, {})
        
        combined_lap = {
            'driver_number': lap['driver_number'],
            'lap_number': lap['lap_number'],
            'i1_speed': lap['i1_speed'],
            'i2_speed': lap['i2_speed'],
            'is_pit_out_lap': lap['is_pit_out_lap'],
            'duration_sector_1': lap['duration_sector_1'],
            'duration_sector_2': lap['duration_sector_2'],
            'duration_sector_3': lap['duration_sector_3'],
            'compound': stint_info.get('compound'),
            'stint_number': stint_info.get('stint_number'),
            'tyre_age_at_start': stint_info.get('tyre_age_at_start')
        }
        combined_data.append(combined_lap)
    
    return combined_data

if __name__ == '__main__':
    practice_1_test_session_key = '7765'
    
    p1_lap_data = practice_session_combined_data(practice_1_test_session_key)

    print(get_session_lap_data(practice_1_test_session_key)[0])
    print(get_session_stint_data(practice_1_test_session_key)[0])

    for lap in p1_lap_data:
        print(lap)