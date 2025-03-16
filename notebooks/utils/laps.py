import requests
import pandas as pd
from collections import defaultdict

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
    
    # Drop where compound is UNKNOWN
    combined_data = [lap for lap in combined_data if lap['compound'] != 'UNKNOWN']

    return combined_data

def combine_all_practices(practice_sessions):
    """
    Combines all practice sessions into a single json object
    """
    combined_data = []
    for session in practice_sessions:
        combined_data.extend(session)

    # Drop all rows where 'is_pit_out_lap' is True
    combined_data = [lap for lap in combined_data if lap['is_pit_out_lap'] == False]

    return combined_data

def extract_data_from_session(laps):
    """
    Extracts key metrics for each driver from session lap data
    
    Args:
        laps (list): List of lap dictionaries containing timing and stint data
    
    Returns:
        pandas.DataFrame: DataFrame containing driver metrics
    """
    
    # Group laps by driver
    driver_laps = defaultdict(list)
    for lap in laps:
        driver_laps[lap['driver_number']].append(lap)
        
    results = []
    for driver, driver_data in driver_laps.items():
        
        # Initialize metrics
        metrics = {'driver_number': driver}
        compounds = set(lap['compound'] for lap in driver_data if lap['compound'])
        
        # Overall fastest lap - filter out laps with None sector times
        valid_laps = [lap for lap in driver_data if None not in (lap['duration_sector_1'], lap['duration_sector_2'], lap['duration_sector_3'])]
        if valid_laps:
            fastest_lap = min(valid_laps, key=lambda x: sum([x['duration_sector_1'], x['duration_sector_2'], x['duration_sector_3']]))
            metrics['fastest_lap_time'] = sum([fastest_lap['duration_sector_1'], fastest_lap['duration_sector_2'], fastest_lap['duration_sector_3']])
            metrics['fastest_lap_compound'] = fastest_lap['compound']
            metrics['fastest_lap_tyre_age'] = fastest_lap['tyre_age_at_start']
            
            # Calculate average lap time
            lap_times = [sum([lap['duration_sector_1'], lap['duration_sector_2'], lap['duration_sector_3']]) for lap in valid_laps]
            metrics['avg_lap_time'] = sum(lap_times) / len(lap_times) if lap_times else None
        
        # Best sectors and speeds - filter out None values
        metrics['best_s1'] = min((lap['duration_sector_1'] for lap in driver_data if lap['duration_sector_1'] is not None), default=None)
        metrics['best_s2'] = min((lap['duration_sector_2'] for lap in driver_data if lap['duration_sector_2'] is not None), default=None)
        metrics['best_s3'] = min((lap['duration_sector_3'] for lap in driver_data if lap['duration_sector_3'] is not None), default=None)
        
        # Average sectors
        valid_s1 = [lap['duration_sector_1'] for lap in driver_data if lap['duration_sector_1'] is not None]
        valid_s2 = [lap['duration_sector_2'] for lap in driver_data if lap['duration_sector_2'] is not None]
        valid_s3 = [lap['duration_sector_3'] for lap in driver_data if lap['duration_sector_3'] is not None]
        metrics['avg_s1'] = sum(valid_s1) / len(valid_s1) if valid_s1 else None
        metrics['avg_s2'] = sum(valid_s2) / len(valid_s2) if valid_s2 else None
        metrics['avg_s3'] = sum(valid_s3) / len(valid_s3) if valid_s3 else None
        
        if all(x is not None for x in [metrics['best_s1'], metrics['best_s2'], metrics['best_s3']]):
            metrics['theoretical_best'] = metrics['best_s1'] + metrics['best_s2'] + metrics['best_s3']
        else:
            metrics['theoretical_best'] = None
        
        metrics['best_i1_speed'] = max((lap['i1_speed'] for lap in driver_data if lap['i1_speed'] is not None), default=None)
        metrics['best_i2_speed'] = max((lap['i2_speed'] for lap in driver_data if lap['i2_speed'] is not None), default=None)
        
        valid_i1_speeds = [lap['i1_speed'] for lap in driver_data if lap['i1_speed'] is not None]
        valid_i2_speeds = [lap['i2_speed'] for lap in driver_data if lap['i2_speed'] is not None]
        metrics['avg_i1_speed'] = sum(valid_i1_speeds) / len(valid_i1_speeds) if valid_i1_speeds else None
        metrics['avg_i2_speed'] = sum(valid_i2_speeds) / len(valid_i2_speeds) if valid_i2_speeds else None
        
        # Lap counts
        metrics['total_laps'] = len(driver_data)
        
        # Per compound analysis
        for compound in compounds:
            compound_laps = [lap for lap in driver_data if lap['compound'] == compound]
            
            # Skip if no laps on compound
            if not compound_laps:
                continue
                
            # Fastest lap on compound - filter out laps with None sector times
            valid_compound_laps = [lap for lap in compound_laps if None not in (lap['duration_sector_1'], lap['duration_sector_2'], lap['duration_sector_3'])]
            if valid_compound_laps:
                fastest_compound_lap = min(valid_compound_laps, key=lambda x: sum([x['duration_sector_1'], x['duration_sector_2'], x['duration_sector_3']]))
                metrics[f'fastest_lap_{compound}'] = sum([fastest_compound_lap['duration_sector_1'],
                                                        fastest_compound_lap['duration_sector_2'],
                                                        fastest_compound_lap['duration_sector_3']])
                metrics[f'fastest_lap_tyre_age_{compound}'] = fastest_compound_lap['tyre_age_at_start']
                
                # Calculate average lap time for compound
                compound_lap_times = [sum([lap['duration_sector_1'], lap['duration_sector_2'], lap['duration_sector_3']]) 
                                    for lap in valid_compound_laps]
                metrics[f'avg_lap_time_{compound}'] = sum(compound_lap_times) / len(compound_lap_times) if compound_lap_times else None
            
            # Best sectors on compound - filter out None values
            metrics[f'best_s1_{compound}'] = min((lap['duration_sector_1'] for lap in compound_laps if lap['duration_sector_1'] is not None), default=None)
            metrics[f'best_s2_{compound}'] = min((lap['duration_sector_2'] for lap in compound_laps if lap['duration_sector_2'] is not None), default=None) 
            metrics[f'best_s3_{compound}'] = min((lap['duration_sector_3'] for lap in compound_laps if lap['duration_sector_3'] is not None), default=None)
            
            # Calculate theoretical best for compound
            if all(x is not None for x in [metrics[f'best_s1_{compound}'], metrics[f'best_s2_{compound}'], metrics[f'best_s3_{compound}']]): 
                metrics[f'theoretical_best_{compound}'] = metrics[f'best_s1_{compound}'] + metrics[f'best_s2_{compound}'] + metrics[f'best_s3_{compound}']
            else:
                metrics[f'theoretical_best_{compound}'] = None
            
            # Average sectors on compound
            valid_s1 = [lap['duration_sector_1'] for lap in compound_laps if lap['duration_sector_1'] is not None]
            valid_s2 = [lap['duration_sector_2'] for lap in compound_laps if lap['duration_sector_2'] is not None]
            valid_s3 = [lap['duration_sector_3'] for lap in compound_laps if lap['duration_sector_3'] is not None]
            metrics[f'avg_s1_{compound}'] = sum(valid_s1) / len(valid_s1) if valid_s1 else None
            metrics[f'avg_s2_{compound}'] = sum(valid_s2) / len(valid_s2) if valid_s2 else None
            metrics[f'avg_s3_{compound}'] = sum(valid_s3) / len(valid_s3) if valid_s3 else None
            
            # Lap count on compound
            metrics[f'laps_{compound}'] = len(compound_laps)
            
        results.append(metrics)

    results_df = pd.DataFrame(results)
        
    return results_df

def create_ran_flags(practice_statistics):
    """
    Creates ran flags for each compound

    Args:
        practice_statistics (pandas.DataFrame): DataFrame containing practice statistics

    Returns:
        pandas.DataFrame: DataFrame containing practice statistics with ran flags
    """
    compounds = set()
    for col in practice_statistics.columns:
        if col.startswith('laps_'):
            compounds.add(col.replace('laps_', ''))

    for compound in compounds:
        compound_cols = [col for col in practice_statistics.columns if col.endswith(f'_{compound}')]
        
        # For each row, check if all values in compound_cols are NaN
        for index, row in practice_statistics.iterrows():
            if row[compound_cols].isna().all():
                practice_statistics.loc[index, f'ran_{compound}'] = False
            else:
                practice_statistics.loc[index, f'ran_{compound}'] = True

    return practice_statistics

def fill_not_ran_nan(practice_statistics):
    """
    Fills NaN values with 0 for columns that are not ran

    Args:
        practice_statistics (pandas.DataFrame): DataFrame containing practice statistics

    Returns:
        pandas.DataFrame: DataFrame containing practice statistics with NaN values filled with 0
    """
    # Get all columns beginning with ran_
    ran_cols = [col for col in practice_statistics.columns if col.startswith('ran_')]

    for col in ran_cols:
        compound = col.replace('ran_', '')
        compound_cols = [col for col in practice_statistics.columns if compound in col and not col.startswith('ran_')]

        # For each row, if the compound_cols are all NaN, set the relevant compound columns for that row to 0
        for index, row in practice_statistics.iterrows():
            if row[compound_cols].isna().all():
                for col in compound_cols:
                    practice_statistics.loc[index, col] = 0

    return practice_statistics

def add_statistic_differentials_per_event(event_practice_statistics):
    """Calculate overall statistics, maxs, mins, averages, ranges, etc. to calculate differences to be applied to the overall dataframe
    
    Args:
        event_practice_statistics (pandas.DataFrame): DataFrame containing practice statistics

    Returns:
        pandas.DataFrame: DataFrame containing practice statistics with added statistic differentials
    """
    # Get numerical columns programmatically, excluding driver_number
    numerical_cols = event_practice_statistics.select_dtypes(include=['int64', 'float64']).columns
    numerical_cols = [col for col in numerical_cols if col != 'driver_number' and 'tyre_age' not in col]

    # Calculate statistics for each numerical column
    for col in numerical_cols:
        # Skip columns that are all zeros or NaN
        if event_practice_statistics[col].sum() == 0 or event_practice_statistics[col].isna().all():
            continue
            
        # Calculate statistics
        col_median = event_practice_statistics[col].median()
        col_min = event_practice_statistics[col].min()
        col_max = event_practice_statistics[col].max()
        col_mean = event_practice_statistics[col].mean()
        
        # Calculate differentials
        event_practice_statistics[f'{col}_diff_to_event_median'] = event_practice_statistics[col] - col_median
        event_practice_statistics[f'{col}_diff_to_event_min'] = event_practice_statistics[col] - col_min
        event_practice_statistics[f'{col}_diff_to_event_max'] = event_practice_statistics[col] - col_max
        event_practice_statistics[f'{col}_diff_to_event_mean'] = event_practice_statistics[col] - col_mean
        
        # Calculate percentage differentials
        event_practice_statistics[f'{col}_pct_diff_to_event_median'] = (event_practice_statistics[col] - col_median) / col_median * 100
        event_practice_statistics[f'{col}_pct_diff_to_event_min'] = (event_practice_statistics[col] - col_min) / col_min * 100
        event_practice_statistics[f'{col}_pct_diff_to_event_max'] = (event_practice_statistics[col] - col_max) / col_max * 100
        event_practice_statistics[f'{col}_pct_diff_to_event_mean'] = (event_practice_statistics[col] - col_mean) / col_mean * 100

    return event_practice_statistics

if __name__ == '__main__':
    practice_1_test_session_key = '7765'
    practice_2_test_session_key = '7766'
    practice_3_test_session_key = '7767'

    p1_lap_data = practice_session_combined_data(practice_1_test_session_key)
    p2_lap_data = practice_session_combined_data(practice_2_test_session_key)
    p3_lap_data = practice_session_combined_data(practice_3_test_session_key)

    combined_practice_data = combine_all_practices([p1_lap_data, p2_lap_data, p3_lap_data])
    practice_statistics = extract_data_from_session(combined_practice_data)
    practice_statistics = create_ran_flags(practice_statistics)
    practice_statistics = fill_not_ran_nan(practice_statistics)

    print(practice_statistics)
