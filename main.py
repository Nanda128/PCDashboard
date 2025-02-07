from flask import Flask, render_template, redirect, url_for
from utils import get_remote_running_applications, terminate_remote_processes_by_name
import json

app = Flask(__name__)

with open('config.json') as config_file:
    config = json.load(config_file)
    config_file.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/processes')
def processes():
    processes = get_remote_running_applications()
    return render_template('processes.html', processes=processes)

@app.route('/terminate/<string:process_name>', methods=['POST'])
def terminate(process_name):
    terminate_remote_processes_by_name(process_name)
    return redirect(url_for('processes'))

if __name__ == '__main__':
    app.run(debug=True)