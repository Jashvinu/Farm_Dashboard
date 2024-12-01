import requests
from datetime import datetime

def get_weather_data(lat, lon, api_key):
    """
    Fetch and format weather data for a given location
    
    Args:
        lat (float): Latitude
        lon (float): Longitude
        api_key (str): OpenWeatherMap API key
    
    Returns:
        dict: Formatted weather data or None if there's an error
    """
    
    url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}'
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        weather_data = response.json()
        
        # Convert timestamps
        report_timestamp = datetime.utcfromtimestamp(weather_data['dt'])
        sunrise_time = datetime.utcfromtimestamp(weather_data['sys']['sunrise'])
        sunset_time = datetime.utcfromtimestamp(weather_data['sys']['sunset'])
        
        # Convert to local time (IST)
        timezone_offset = weather_data['timezone']  # seconds
        local_report_time = datetime.utcfromtimestamp(weather_data['dt'] + timezone_offset)
        local_sunrise = datetime.utcfromtimestamp(weather_data['sys']['sunrise'] + timezone_offset)
        local_sunset = datetime.utcfromtimestamp(weather_data['sys']['sunset'] + timezone_offset)
        
        # Format the data
        formatted_data = {
            'timestamp': {
                'utc': report_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'local': local_report_time.strftime('%Y-%m-%d %H:%M:%S'),
                'sunrise': local_sunrise.strftime('%H:%M:%S'),
                'sunset': local_sunset.strftime('%H:%M:%S')
            },
            'location': {
                'name': weather_data['name'],
                'country': weather_data['sys']['country']
            },
            'temperature': {
                'current': round(weather_data['main']['temp'] - 273.15, 1),
                'feels_like': round(weather_data['main']['feels_like'] - 273.15, 1),
                'min': round(weather_data['main']['temp_min'] - 273.15, 1),
                'max': round(weather_data['main']['temp_max'] - 273.15, 1)
            },
            'conditions': {
                'main': weather_data['weather'][0]['main'],
                'description': weather_data['weather'][0]['description'],
                'humidity': weather_data['main']['humidity'],
                'pressure': weather_data['main']['pressure']
            },
            'wind': {
                'speed': weather_data['wind']['speed'],
                'direction': weather_data['wind'].get('deg', 'N/A')
            },
            'clouds': {
                'coverage': weather_data['clouds']['all']
            }
        }
        
        # Add rainfall data if available
        if 'rain' in weather_data:
            formatted_data['rain'] = {
                'last_1h': weather_data['rain'].get('1h', 0),
                'last_3h': weather_data['rain'].get('3h', 0)
            }
            
        return formatted_data
        
    except requests.RequestException as e:
        print(f"Error making API request: {e}")
        return None
    except KeyError as e:
        print(f"Error parsing weather data: {e}")
        return None