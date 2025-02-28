from flask import Flask, render_template, request, flash, session
from markupsafe import Markup
import json
import plotly.graph_objs as go
from db import save_processes_to_db, fetch_latest_data_from_db
from weather import get_lat_lon, fetch_weather_data
import time

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
        data = request.get_json()
        if not data:
            raise ValueError('No JSON data received')
        process_data = data['processes'] if 'processes' in data else []
        ram_usage = data['ram_usage'] if 'ram_usage' in data else None
        save_processes_to_db(config, process_data, ram_usage)
        flash('Processes data successfully saved to the database.', 'success')
    except (ValueError, json.JSONDecodeError) as e:
        flash(f'Error processing JSON data: {e}', 'error')
    except Exception as e:
        flash(f'Error: {e}', 'error')
    return 'OK', 200

def handle_get_request():
    try:
        data = fetch_latest_data_from_db(config)
        process_data = json.loads(data[0]['processes']) if data else {}
        ram_usage = data[0]['ram_usage'] if data else None

        if not process_data:
            flash('No processes found in the database.', 'info')
        if ram_usage is None:
            flash('No RAM usage data found in the database.', 'info')

        gauge = generate_ram_gauge(ram_usage) if ram_usage is not None else None
        gauge_html = Markup(gauge.to_html(full_html=False)) if gauge else None
    except Exception as e:
        flash(f'Error: {e}', 'error')
        process_data = {}
        gauge_html = None
    return render_template('processes.html', processes=process_data, gauge_html=gauge_html)

def generate_ram_gauge(ram_usage):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=ram_usage,
        title={'text': "RAM Usage"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 50], 'color': "green"},
                {'range': [50, 75], 'color': "yellow"},
                {'range': [75, 100], 'color': "red"}
            ]
        }
    ))
    return fig

@app.route('/weather', methods=['GET', 'POST'])
def weather():
    api_key = config['Weather']['api_key']
    city, units, approach = get_city_units_approach()
    lat, lon = get_lat_lon(api_key, city)
    start_time = time.time()
    use_db = approach == 'db-full'
    weather_data, error = fetch_weather_data(api_key, lat, lon, units, use_db, config, city) if lat and lon else (None, "City not found")
    time_taken = int((time.time() - start_time) * 1000)
    return render_template('weather.html', weather=weather_data, selected_city=city, selected_units=units, selected_approach=approach, error=error, time_taken=time_taken)

def get_city_units_approach():
    if request.method == 'POST':
        city = request.form['city']
        units = request.form['units']
        approach = request.form['approach']
        session['last_city'] = city
        session['last_units'] = units
        session['last_approach'] = approach
    else:
        city = session.get('last_city', config['Weather']['default_city'])
        units = session.get('last_units', config['Weather']['default_units'])
        approach = session.get('last_approach', 'db-less')
    return city, units, approach

if __name__ == '__main__':
    app.run(debug=True)