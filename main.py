from flask import Flask, render_template, request, redirect, url_for, flash
import requests
import json

app = Flask(__name__)
app.secret_key = 'ubersecretkey'  # Needed for flashing messages

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/processes')
def processes():
    try:
        client_ip = request.headers.get('X-Real-IP')
        response = requests.get(f'http://{client_ip}:{remote_user_port}/get_running_applications')
        response.raise_for_status()
        processes = response.json()
    except requests.exceptions.RequestException as e:
        flash(f'Error fetching processes: {e}', 'error')
        processes = {}
    except json.JSONDecodeError:
        flash('Error decoding JSON response from server', 'error')
        processes = {}
    return render_template('processes.html', processes=processes)

@app.route('/terminate/<string:process_name>', methods=['POST'])
def terminate(process_name):
    try:
        client_ip = request.headers.get('X-Real-IP')
        process_data = json.dumps({'process_name': process_name})
        response = requests.post(f'http://{client_ip}:{remote_user_port}/terminate_processes', json=process_data)
        response.raise_for_status()
        flash(f'Successfully terminated processes with name: {process_name}', 'success')
    except requests.exceptions.RequestException as e:
        flash(f'Error terminating processes: {e}', 'error')
    return redirect(url_for('processes'))

with open('mysite/config.json') as config_file:
    config = json.load(config_file)
    remote_user_port = config['RemoteUser']['Port']
    config_file.close()

if __name__ == '__main__':
    app.run(debug=True)