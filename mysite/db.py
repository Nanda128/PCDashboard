import mysql.connector
import json

class DatabaseConnection:
    def __init__(self, config, db_type):
        self.config = config
        self.db_type = db_type
        self.connection = None

    def __enter__(self):
        db_config = self.config[self.db_type]
        self.connection = mysql.connector.connect(
            host=db_config['host'],
            database=db_config['database'],
            user=db_config['user'],
            password=db_config['password']
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
    with DatabaseConnection(config, 'ProcessDatabase') as connection:
        with DatabaseCursor(connection) as cursor:
            add_process = "INSERT INTO process_data (processes, ram_usage) VALUES (%s, %s)"
            cursor.execute(add_process, (json.dumps(processes), ram_usage))
            connection.commit()

def fetch_latest_data_from_db(config):
    with DatabaseConnection(config, 'ProcessDatabase') as connection:
        with DatabaseCursor(connection) as cursor:
            cursor.execute("SELECT processes, ram_usage FROM process_data ORDER BY created_at DESC LIMIT 1")
            result = cursor.fetchall()
            return result if result else {}

def save_weather_to_db(config, city, units, data):
    with DatabaseConnection(config, 'WeatherDatabase') as connection:
        with DatabaseCursor(connection) as cursor:
            add_weather = "INSERT INTO weather_data (city, units, data) VALUES (%s, %s, %s)"
            cursor.execute(add_weather, (city, units, json.dumps(data)))
            connection.commit()

def fetch_weather_from_db(config, city, units):
    with DatabaseConnection(config, 'WeatherDatabase') as connection:
        with DatabaseCursor(connection) as cursor:
            cursor.execute("SELECT data FROM weather_data WHERE city = %s AND units = %s ORDER BY created_at DESC LIMIT 1", (city, units))
            result = cursor.fetchone()
            return json.loads(result['data']) if result else None