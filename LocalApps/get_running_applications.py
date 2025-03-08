import psutil
from logger import LoggerManager
import json
import requests
import time
import os

logger = LoggerManager().get_logger()
running = True

def get_running_processes():
    processes = {}
    for p in psutil.process_iter(['pid', 'name']):
        try:
            name, pid = p.info['name'], p.info['pid']
            if name and pid != 0:
                processes.setdefault(name, []).append(pid)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
            logger.error('Failed to retrieve process information. Error: %s', e)
    logger.info('Retrieved running applications!')
    return processes

def get_ram_usage():
    ram_usage = psutil.virtual_memory()
    return ram_usage.percent if ram_usage else None

def get_battery_percentage():
    battery = psutil.sensors_battery()
    return battery.percent if battery else None

script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, '../mysite/config.json')

with open(config_path) as config_file:
    url = json.load(config_file)['Server']['host']
    logger.info(f'Loaded URL from config.json: {url}')

previous_processes = {}
previous_battery_percentage = None

try:
    while running:
        processes = get_running_processes()
        ram_usage = get_ram_usage()
        battery_percentage = get_battery_percentage()
        
        if processes != previous_processes or battery_percentage != previous_battery_percentage:
            data = {
                "processes": processes,
                "ram_usage": ram_usage,
                "battery_percentage": battery_percentage
            }
            try:
                logger.info(f'Sending processes, RAM usage, and battery percentage data to {url}')
                response = requests.post(f"{url}/processes", json=data, timeout=10)
                response.raise_for_status()
                logger.info(f'Successfully sent processes, RAM usage, and battery percentage data to {url}')
                previous_processes = processes
                previous_battery_percentage = battery_percentage
            except requests.RequestException as e:
                logger.error(f'Failed to send data to {url}: {e}')
        time.sleep(10)
except KeyboardInterrupt:
    logger.info('Stopping the application...')
    running = False