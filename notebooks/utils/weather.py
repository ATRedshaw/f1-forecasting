import requests

def get_weather_by_session_keys(session_keys):
    """
    Gets the weather data for given session keys

    Args:
        session_keys (list): List of session keys to get weather data for

    Returns:
        dict: Dictionary containing weather statistics across all sessions
    """
    weather_data = []
    
    # Get weather data for each session key
    for session_key in session_keys:
        response = requests.get(f'https://api.openf1.org/v1/weather?session_key={session_key}')
        if response.status_code == 200:
            weather_data.extend(response.json())
            
    if not weather_data:
        return None

    # Initialize stats dictionary
    stats = {
        'air_temperature': {'min': None, 'max': None, 'avg': None, 'median': None},
        'humidity': {'min': None, 'max': None, 'avg': None, 'median': None}, 
        'pressure': {'min': None, 'max': None, 'avg': None, 'median': None},
        'rainfall': {'min': None, 'max': None, 'avg': None, 'median': None},
        'track_temperature': {'min': None, 'max': None, 'avg': None, 'median': None},
        'wind_speed': {'min': None, 'max': None, 'avg': None, 'median': None}
    }

    # Return empty stats if no data
    if not weather_data:
        return stats

    # Calculate stats for each metric
    for metric in stats.keys():
        values = [float(x[metric]) for x in weather_data if metric in x and x[metric] is not None]
        if values:
            stats[metric]['min'] = min(values)
            stats[metric]['max'] = max(values)
            stats[metric]['avg'] = sum(values) / len(values)
            stats[metric]['median'] = sorted(values)[len(values)//2]

    return stats