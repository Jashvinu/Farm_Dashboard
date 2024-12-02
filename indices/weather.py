import requests
import json


def get_agromonitoring_weather(latitude, longitude, api_key):
    base_url = "https://agromonitoring.com/api/current-weather"
    params = {
        'lat': latitude,
        'lon': longitude,
        'appid': api_key
    }

    response = requests.get(base_url, params=params)

# ... (rest of your code)

    if response.status_code == 200:
        try:
            return response.json()
        except json.JSONDecodeError:
            return {'error': 'Invalid JSON response from API'}
    else:
        return {'error': f'API request failed with status code: {response.status_code}'}
    # Indicate an error occurred

# Get your Agromonitoring API key (https://agromonitoring.com/api)
your_api_key = "4f58b19da6da89c1960b05f630be5e87" 

latitude = 12.392392  # Example latitude
longitude = 77.773332  # Example longitude

weather_data = get_agromonitoring_weather(latitude, longitude, your_api_key)

if weather_data:
    # Example of accessing data
    print(weather_data)
    #print(f"Temperature: {weather_data['temp']} Celsius")
    #print(f"Description: {weather_data['weather'][0]['description']}")
    # ... Access other weather data as needed
else:
    print("An error occurred. Please check your coordinates or API key.")
