import requests

def get_lat_lon(api_key, city):
    url = f'http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={api_key}'
    response = requests.get(url)
    if response.status_code == 200 and response.json():
        data = response.json()[0]
        return data['lat'], data['lon']
    return None, None

def fetch_weather_data(api_key, lat, lon, units):
    url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units={units}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json(), None
    return None, "Unable to fetch weather data"
