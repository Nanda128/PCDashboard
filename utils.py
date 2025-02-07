import json
import requests

with open('config.json') as config_file:
    config = json.load(config_file)
    remote_user_ip = config['RemoteUser']['IP']
    remote_user_port = config['RemoteUser']['Port']

def get_remote_running_applications():
    """
    Retrieves a list of currently running applications and their process IDs from a remote user's computer.

    Returns:
        processes: A dictionary where the keys are application names and the values are lists of process IDs.
    """
    response = requests.get(f'http://{remote_user_ip}:{remote_user_port}/get_running_applications')
    processes = response.json()
    return processes

def terminate_remote_processes_by_name(process_name):
    """
    Terminates all processes with a given name on a remote user's computer.

    Args:
        process_name: The name of the process to terminate.
    """
    requests.post(f'http://{remote_user_ip}:{remote_user_port}/terminate_processes', json={'process_name': process_name})