import requests

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

def fetch_weather_data(api_key, lat, lon, units):
    """Fetch weather data from OpenWeatherMap API

    Args:
        api_key : API key for OpenWeatherMap
        lat : latitude of city/location
        lon : longitude of city/location
        units : Imperial/Metric

    Returns:
        response : JSON response from the API if successful
    """
    url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units={units}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json(), None
    return None, "Unable to fetch weather data"
