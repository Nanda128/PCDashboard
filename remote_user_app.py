from flask import Flask, request, jsonify
import psutil
from logger import LoggerManager

logger = LoggerManager().get_logger()

app = Flask(__name__)

@app.route('/get_running_applications', methods=['GET'])
def get_running_applications():
    """
    Get a list of running applications and their process IDs.

    Returns:
        processes: JSON response containing a list of running applications and their process IDs.
    """
    processes = {}
    for p in psutil.process_iter(['pid', 'name']):
        try:
            if p.info['name'] and p.info['pid'] != 0:
                if p.info['name'] not in processes:
                    processes[p.info['name']] = []
                processes[p.info['name']].append(p.info['pid'])
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            logger.error('Failed to retrieve process information')
    logger.info('Retrieved running applications!')
    return jsonify(processes)

@app.route('/terminate_processes', methods=['POST'])
def terminate_processes():
    """
    Terminate processes with a given name.

    Returns:
        status: JSON response indicating the status of the operation.
    """
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
                logger.error('Failed to terminate process')
    logger.info('Terminated processes with name: {}'.format(process_name))
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
