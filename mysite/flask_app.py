from flask import Flask, render_template, request, flash, session
import json
from db import save_processes_to_db, fetch_processes_from_db
from weather import get_lat_lon, fetch_weather_data

app = Flask(__name__)
app.secret_key = 'ubersecretkey'  # Needed for flashing messages

@app.template_filter('fromjson')
def fromjson_filter(s):
    return json.loads(s)

CONFIG_PATH = 'mysite/config.json'

def load_config():
    with open(CONFIG_PATH) as config_file:
        return json.load(config_file)

config = load_config()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/processes', methods=['GET', 'POST'])
def processes():
    if request.method == 'POST':
        return handle_post_request()
    return handle_get_request()

def handle_post_request():
    try:
        processes = request.get_json()
        if not processes:
            raise ValueError('No JSON data received')
        save_processes_to_db(config, processes)
        flash('Processes data successfully saved to the database.', 'success')
    except (ValueError, json.JSONDecodeError) as e:
        flash(f'Error processing JSON data: {e}', 'error')
    except Exception as e:
        flash(f'Error: {e}', 'error')
    return render_template('processes.html')

def handle_get_request():
    try:
        processes = fetch_processes_from_db(config)
        if not processes:
            flash('No processes found in the database.', 'info')
    except Exception as e:
        flash(f'Error: {e}', 'error')
        processes = None
    return render_template('processes.html', processes=processes)

@app.route('/weather', methods=['GET', 'POST'])
def weather():
    api_key = config['Weather']['api_key']
    city, units = get_city_and_units()
    lat, lon = get_lat_lon(api_key, city)
    weather_data, error = fetch_weather_data(api_key, lat, lon, units) if lat and lon else (None, "City not found")
    return render_template('weather.html', weather=weather_data, selected_city=city, selected_units=units, error=error)

def get_city_and_units():
    if request.method == 'POST':
        city = request.form['city']
        units = request.form['units']
        session['last_city'] = city
        session['last_units'] = units
    else:
        city = session.get('last_city', config['Weather']['default_city'])
        units = session.get('last_units', config['Weather']['default_units'])
    return city, units

if __name__ == '__main__':
    app.run(debug=True)