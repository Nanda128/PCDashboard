import psutil
import json
import requests
from logger import LoggerManager

logger = LoggerManager().get_logger()

def get_running_applications():
    logger.info('Getting running applications...')
    processes = {}
    for p in psutil.process_iter(['pid', 'name']):
        try:
            if p.info['name'] and p.info['pid'] != 0:
                if p.info['name'] not in processes:
                    processes[p.info['name']] = []
                processes[p.info['name']].append(p.info['pid'])
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            logger.error('Failed to get process information for PID: {}'.format(p.info['pid']))
            pass
    processes_json = json.dumps(processes, indent=4)
    logger.info('Running applications: {}'.format(processes_json))
    return processes

def terminate_processes_by_name(process_name):
    logger.info('Terminating all processes with name: {}'.format(process_name))
    terminated_pids = set()
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == process_name and proc.info['pid'] not in terminated_pids:
            try:
                proc.terminate()
                proc.wait(timeout=3)
                terminated_pids.add(proc.info['pid'])
                logger.info('Process with PID: {} successfully terminated!'.format(proc.info['pid']))
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                logger.error('Failed to terminate process with PID: {}'.format(proc.info['pid']))
                pass

def send_process_data_to_server(process_data, server_url):
    try:
        response = requests.post(server_url, json=process_data)
        if response.status_code == 200:
            logger.info('Process data successfully sent to server.')
        else:
            logger.error('Failed to send process data to server. Status code: {}'.format(response.status_code))
    except requests.RequestException as e:
        logger.error('Exception occurred while sending process data to server: {}'.format(e))
