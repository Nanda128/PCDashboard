import mysql.connector
import json

class DatabaseConnection:
    def __init__(self, config):
        self.config = config
        self.connection = None

    def __enter__(self):
        self.connection = mysql.connector.connect(
            host=self.config['ProcessDatabase']['host'],
            database=self.config['ProcessDatabase']['database'],
            user=self.config['ProcessDatabase']['user'],
            password=self.config['ProcessDatabase']['password']
        )
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            self.connection.close()

class DatabaseCursor:
    def __init__(self, connection):
        self.connection = connection
        self.cursor = None

    def __enter__(self):
        self.cursor = self.connection.cursor(dictionary=True)
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cursor:
            self.cursor.close()

def save_processes_to_db(config, processes, ram_usage):
    with DatabaseConnection(config) as connection:
        with DatabaseCursor(connection) as cursor:
            add_process = "INSERT INTO process_data (processes, ram_usage) VALUES (%s, %s)"
            cursor.execute(add_process, (json.dumps(processes), ram_usage))
            connection.commit()

def fetch_latest_data_from_db(config):
    with DatabaseConnection(config) as connection:
        with DatabaseCursor(connection) as cursor:
            cursor.execute("SELECT processes, ram_usage FROM process_data ORDER BY created_at DESC LIMIT 1")
            result = cursor.fetchall()
            return result if result else {}