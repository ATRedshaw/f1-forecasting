import requests
import pandas as pd

def get_end_positions(session_key):
    # Get position data
    url = f'https://api.openf1.org/v1/position?session_key={session_key}'
    response = requests.get(url)
    position_data = response.json()

    # Create dictionary to store latest position for each driver
    latest_positions = {}
    for entry in position_data:
        driver = entry['driver_number']
        position = entry['position'] 
        # Update dictionary - will keep overwriting with latest position
        latest_positions[driver] = position

    # Convert to dataframe
    positions_df = pd.DataFrame(list(latest_positions.items()), columns=['driver_number', 'position'])

    return positions_df
