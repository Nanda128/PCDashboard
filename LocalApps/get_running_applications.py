import psutil
from logger import LoggerManager
import json
import requests

logger = LoggerManager().get_logger()

processes = {}
for p in psutil.process_iter(['pid', 'name']):
    try:
        name, pid = p.info['name'], p.info['pid']
        if name and pid != 0:
            processes.setdefault(name, []).append(pid)
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        logger.error('Failed to retrieve process information')    
logger.info('Retrieved running applications!')

with open('config.json') as config_file:
    url = json.load(config_file)['Server']['host']
    logger.info(f'Loaded URL from config.json: {url}')

try:
    logger.info(f'Sending processes data to {url}')
    response = requests.post(f"{url}/processes", json=processes, timeout=10)
    response.raise_for_status()
    logger.info(f'Successfully sent processes data to {url}')
except requests.RequestException as e:
    logger.error(f'Failed to send processes data to {url}: {e}')