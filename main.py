from flask import Flask, render_template, request, redirect, url_for
from utils import get_running_applications, terminate_processes_by_name
from logger import LoggerManager
import psutil

logger = LoggerManager().get_logger()

app = Flask(__name__)

@app.route('/')
def index():
    logger.info('Rendering index page...')
    return render_template('index.html')

@app.route('/processes')
def processes():
    logger.info('Rendering processes page...')
    processes = get_running_applications()
    return render_template('processes.html', processes=processes)

@app.route('/terminate/<int:pid>', methods=['POST'])
def terminate(pid):
    logger.info('Terminating process with PID: {}'.format(pid))
    try:
        p = psutil.Process(pid)
        process_name = p.name()
        logger.info('Process name to terminate: {}'.format(process_name))
        terminate_processes_by_name(process_name)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        logger.error('Failed to find process with PID: {}'.format(pid))
        pass
    return redirect(url_for('processes'))

if __name__ == '__main__':
    logger.info('Web App successfully started!')
    app.run(debug=True)