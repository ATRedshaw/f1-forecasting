import json
import pandas as pd

def retrieve_previous_n_events(position_history, last_n_events=1):
    qualifying_events = []
    race_events = []
    # Directly use last_n_events as an integer

    try:
        # If last_n_events is -1, use all events, otherwise use the last n events
        if last_n_events == -1:
            event_keys = list(position_history.keys())
        else:
            event_keys = list(position_history.keys())[-last_n_events:]
    except:
        return [], []
    
    for event_key in event_keys:
        if event_key in position_history:
            qualifying_events.append(position_history[event_key]['qualifying'])
            race_events.append(position_history[event_key]['race'])

    return qualifying_events, race_events

def aggregate_previous_n_events(qualifying_events, race_events, n_value):
    # Initialize empty lists to store all positions for each driver
    all_data = {}

    if n_value == -1:
        n_value = "career"
    
    # Process each event
    for i in range(len(qualifying_events)):
        quali = qualifying_events[i]
        race = race_events[i]
        
        # Create lookup dicts for this event
        quali_dict = {d['driver']: d['position'] for d in quali}
        race_dict = {d['driver']: d['position'] for d in race}
        
        # Calculate positions gained/lost
        for driver in quali_dict:
            if driver not in all_data:
                all_data[driver] = {
                    'quali_positions': [],
                    'race_positions': [],
                    'positions_gained': []
                }
            
            # Store positions
            if driver in race_dict:
                all_data[driver]['quali_positions'].append(quali_dict[driver])
                all_data[driver]['race_positions'].append(race_dict[driver])
                all_data[driver]['positions_gained'].append(quali_dict[driver] - race_dict[driver])
    
    # Calculate aggregated statistics
    aggregated_stats = []
    for driver, data in all_data.items():
        if len(data['quali_positions']) > 0:
            stats = {
                'driver_number': driver,
                f'previous_{n_value}_quali_min': min(data['quali_positions']),
                f'previous_{n_value}_quali_max': max(data['quali_positions']),
                f'previous_{n_value}_quali_avg': sum(data['quali_positions']) / len(data['quali_positions']),
                f'previous_{n_value}_race_min': min(data['race_positions']),
                f'previous_{n_value}_race_max': max(data['race_positions']),
                f'previous_{n_value}_race_avg': sum(data['race_positions']) / len(data['race_positions']),
                f'previous_{n_value}_positions_gained_min': min(data['positions_gained']),
                f'previous_{n_value}_positions_gained_max': max(data['positions_gained']),
                f'previous_{n_value}_positions_gained_avg': sum(data['positions_gained']) / len(data['positions_gained']),
                f'previous_{n_value}_consistency_quali': max(data['quali_positions']) - min(data['quali_positions']),
                f'previous_{n_value}_consistency_race': max(data['race_positions']) - min(data['race_positions']),
                f'previous_{n_value}_n_races': len(data['race_positions'])
            }
            aggregated_stats.append(stats)
            
    return pd.DataFrame(aggregated_stats)

def add_previous_n_events(practice_statistics, previous_n_events_df, n_value):
    if n_value == -1:
        n_value = "career"

    # Add flag for previous appearances before merge
    practice_statistics[f'previous_{n_value}_did_appear'] = practice_statistics['driver_number'].isin(previous_n_events_df['driver_number']).astype(bool)
    
    # Merge the dataframes
    practice_statistics = practice_statistics.merge(previous_n_events_df, on='driver_number', how='left')

    return practice_statistics

if __name__ == "__main__":
    position_history = json.load(open('notebooks/data/position_history.json'))
    position_history = []
    previous_n_events = 3
    qualifying_events, race_events = retrieve_previous_n_events(position_history, previous_n_events)
    aggregated_stats = aggregate_previous_n_events(qualifying_events, race_events, previous_n_events)
    print(aggregated_stats)
