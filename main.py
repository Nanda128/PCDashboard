from flask import Flask, render_template, request, flash, jsonify
import json
import mysql.connector
from jinja2 import Environment

app = Flask(__name__)
app.secret_key = 'ubersecretkey'  # Needed for flashing messages

with open('mysite/config.json') as config_file:
    config = json.load(config_file)

# Custom filter to parse JSON
def from_json(value):
    return json.loads(value)

app.jinja_env.filters['fromjson'] = from_json

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/processes', methods=['GET', 'POST'])
def processes():
    if request.method == 'POST':
        try:
            processes = request.get_json()
            if not processes:
                raise ValueError('No JSON data received')

            connection = mysql.connector.connect(
                host=config['Database']['host'],
                database=config['Database']['database'],
                user=config['Database']['user'],
                password=config['Database']['password']
            )
            cursor = connection.cursor()
            add_process = ("INSERT INTO process_data (processes) VALUES (%s)")
            cursor.execute(add_process, (json.dumps(processes),))
            connection.commit()
            flash('Processes data successfully saved to the database.', 'success')
        except (ValueError, json.JSONDecodeError) as e:
            flash(f'Error processing JSON data: {e}', 'error')
            processes = {}
        except mysql.connector.Error as err:
            flash(f'Error connecting to the database: {err}', 'error')
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    else: #Request method is GET
        try:
            connection = mysql.connector.connect(
                host=config['Database']['host'],
                database=config['Database']['database'],
                user=config['Database']['user'],
                password=config['Database']['password']
            )
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT processes FROM process_data ORDER BY created_at DESC")
            result = cursor.fetchall()
            if result:
                processes = result
            else:
                processes = None
                flash('No processes found in the database.', 'info')
        except mysql.connector.Error as err:
            processes = None
            flash(f'Error connecting to the database: {err}', 'error')
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return render_template('processes.html', processes=processes)

if __name__ == '__main__':
    app.run(debug=True)