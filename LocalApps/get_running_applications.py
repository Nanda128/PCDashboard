import psutil
from logger import LoggerManager
import json
import requests
import time
import os

logger = LoggerManager().get_logger()

def get_running_processes():
    processes = {}
    for p in psutil.process_iter(['pid', 'name']):
        try:
            name, pid = p.info['name'], p.info['pid']
            if name and pid != 0:
                processes.setdefault(name, []).append(pid)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            logger.error('Failed to retrieve process information. Error: %s', e)
    logger.info('Retrieved running applications!')
    return processes

def get_ram_usage():
    return psutil.virtual_memory().percent

script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, '../mysite/config.json')

with open(config_path) as config_file:
    url = json.load(config_file)['Server']['host']
    logger.info(f'Loaded URL from config.json: {url}')

while True:
    processes = get_running_processes()
    ram_usage = get_ram_usage()
    data = {
        "processes": processes,
        "ram_usage": ram_usage
    }
    try:
        logger.info(f'Sending processes and RAM usage data to {url}')
        response = requests.post(f"{url}/processes", json=data, timeout=10)
        response.raise_for_status()
        logger.info(f'Successfully sent processes and RAM usage data to {url}')
    except requests.RequestException as e:
        logger.error(f'Failed to send processes and RAM usage data to {url}: {e}')
    time.sleep(10)