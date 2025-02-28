import requests
from db import save_weather_to_db, fetch_weather_from_db

def get_lat_lon(api_key, city):
    """Get latitude and longitude of a city using OpenWeatherMap's Geocoding API

    Args:
        api_key : API key for OpenWeatherMap
        city : Name of the city

    Returns:
        lat: Latitude of the city
        lon: Longitude of the city 
    """
    url = f'http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={api_key}'
    response = requests.get(url)
    if response.status_code == 200 and response.json():
        data = response.json()[0]
        return data['lat'], data['lon']
    return None, None

def fetch_weather_data(api_key, lat, lon, units, use_db, config, city):
    """Fetch weather data from OpenWeatherMap API or database

    Args:
        api_key : API key for OpenWeatherMap
        lat : latitude of city/location
        lon : longitude of city/location
        units : Imperial/Metric
        use_db : Boolean to determine whether to use the database
        config : Configuration dictionary
        city : Name of the city

    Returns:
        response : JSON response from the API or database if successful
    """
    if use_db:
        weather_data = fetch_weather_from_db(config, city, units)
        if weather_data:
            return weather_data, None

    url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units={units}'
    response = requests.get(url)
    if response.status_code == 200:
        weather_data = response.json()
        if use_db:
            save_weather_to_db(config, city, units, weather_data)
        return weather_data, None
    return None, "Unable to fetch weather data"
