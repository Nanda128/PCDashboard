import mysql.connector
import json

def get_db_connection(config):
    return mysql.connector.connect(
        host=config['Database']['host'],
        database=config['Database']['database'],
        user=config['Database']['user'],
        password=config['Database']['password']
    )

def save_processes_to_db(config, processes):
    connection = get_db_connection(config)
    cursor = connection.cursor()
    add_process = "INSERT INTO process_data (processes) VALUES (%s)"
    cursor.execute(add_process, (json.dumps(processes),))
    connection.commit()
    cursor.close()
    connection.close()

def fetch_processes_from_db(config):
    connection = get_db_connection(config)
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT processes FROM process_data ORDER BY created_at DESC")
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result
