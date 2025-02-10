from flask import Flask, request, jsonify
from flask_cors import CORS
import psutil
from logger import LoggerManager

logger = LoggerManager().get_logger()

app = Flask(__name__)
CORS(app)

@app.before_request
def log_request_info():
    logger.debug(f'Received {request.method} request for {request.url}')
    logger.debug(f'Request headers: {request.headers}')
    logger.debug(f'Request body: {request.get_data()}')

@app.route('/get_running_applications', methods=['GET'])
def get_running_applications():
    processes = {}
    for p in psutil.process_iter(['pid', 'name']):
        try:
            name, pid = p.info['name'], p.info['pid']
            if name and pid != 0:
                processes.setdefault(name, []).append(pid)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            logger.error('Failed to retrieve process information')    
    logger.info('Retrieved running applications!')
    return jsonify(processes)

@app.route('/terminate_processes', methods=['POST'])
def terminate_processes():
    data = request.get_json()
    process_name = data.get('process_name')
    terminated_pids = set()
    
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == process_name and proc.info['pid'] not in terminated_pids:
            try:
                proc.terminate()
                proc.wait(timeout=3)
                terminated_pids.add(proc.info['pid'])
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                logger.error(f'Failed to terminate process. Error:', exc_info=True)

    logger.info(f'Terminated processes with name: {process_name}')
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
