from flask import Flask, render_template, request, flash
import json
import mysql.connector

app = Flask(__name__)
app.secret_key = 'ubersecretkey'  # Needed for flashing messages

def load_config():
    with open('mysite/config.json') as config_file:
        return json.load(config_file)

config = load_config()

def get_db_connection():
    return mysql.connector.connect(
        host=config['Database']['host'],
        database=config['Database']['database'],
        user=config['Database']['user'],
        password=config['Database']['password']
    )

def from_json(value):
    return json.loads(value)

app.jinja_env.filters['fromjson'] = from_json

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/processes', methods=['GET', 'POST'])
def processes():
    if request.method == 'POST':
        return handle_post_request()
    elif request.method == 'GET':
        return handle_get_request()

def handle_post_request():
    try:
        processes = request.get_json()
        if not processes:
            raise ValueError('No JSON data received')

        save_processes_to_db(processes)
        flash('Processes data successfully saved to the database.', 'success')
    except (ValueError, json.JSONDecodeError) as e:
        flash(f'Error processing JSON data: {e}', 'error')
    except mysql.connector.Error as err:
        flash(f'Error connecting to the database: {err}', 'error')
    return render_template('processes.html')

def handle_get_request():
    try:
        processes = fetch_processes_from_db()
        if not processes:
            flash('No processes found in the database.', 'info')
    except mysql.connector.Error as err:
        flash(f'Error connecting to the database: {err}', 'error')
        processes = None
    return render_template('processes.html', processes=processes)

def save_processes_to_db(processes):
    connection = get_db_connection()
    cursor = connection.cursor()
    add_process = ("INSERT INTO process_data (processes) VALUES (%s)")
    cursor.execute(add_process, (json.dumps(processes),))
    connection.commit()
    cursor.close()
    connection.close()

def fetch_processes_from_db():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT processes FROM process_data ORDER BY created_at DESC")
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result

if __name__ == '__main__':
    app.run(debug=True)