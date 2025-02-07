from flask import Flask, render_template, redirect, url_for
from utils import get_running_applications, terminate_processes_by_name
import json
from logger import LoggerManager

logger = LoggerManager().get_logger()

app = Flask(__name__)

with open('config.json') as config_file:
    config = json.load(config_file)
    config_file.close()

@app.route('/')
def index():
    logger.info('Rendering index page...')
    return render_template('index.html')

@app.route('/processes')
def processes():
    logger.info('Rendering processes page...')
    processes = get_running_applications()
    return render_template('processes.html', processes=processes)

@app.route('/terminate/<string:process_name>', methods=['POST'])
def terminate(process_name):
    logger.info('Terminating all processes with name: {}'.format(process_name))
    terminate_processes_by_name(process_name)
    return redirect(url_for('processes'))

if __name__ == '__main__':
    logger.info('Web App successfully started!')
    app.run(debug=True)