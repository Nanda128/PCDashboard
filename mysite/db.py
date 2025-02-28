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

def execute_query(config, db_type, query, params=None, fetch_one=False, fetch_all=False):
    """Execute a query on the database

    Args:
        config : Configuration settings from config.json
        db_type : Type of database to connect to
        query : SQL query to execute
        params (optional): Parameters to pass to the query. Defaults to None
        fetch_one (optional): Whether to fetch only one result. Defaults to False
        fetch_all (optional): Whether to fetch all results. Defaults to False

    Returns:
        result : Result of the query if fetch_one or fetch_all is True
    """
    with DatabaseConnection(config, db_type) as connection:
        with DatabaseCursor(connection) as cursor:
            cursor.execute(query, params)
            if fetch_one:
                result = cursor.fetchone()
                return result if result else {}
            if fetch_all:
                result = cursor.fetchall()
                return result if result else []
            connection.commit()

def save_processes_to_db(config, processes, ram_usage):
    """Save process data to the database

    Args:
        config : Configuration settings from config.json
        processes : Dictionary of running processes
        ram_usage : RAM usage percentage
    """
    query = "INSERT INTO process_data (processes, ram_usage) VALUES (%s, %s)"
    execute_query(config, 'ProcessDatabase', query, (json.dumps(processes), ram_usage))

def fetch_latest_data_from_db(config):
    """Fetch the latest process data from the database

    Args:
        config : Configuration settings from config.json

    Returns:
        result : Latest process data
    """
    query = "SELECT processes, ram_usage FROM process_data ORDER BY created_at DESC LIMIT 1"
    return execute_query(config, 'ProcessDatabase', query, fetch_one=True)

def save_weather_to_db(config, city, units, data):
    """Save weather data to the database

    Args:
        config : Configuration settings from config.json
        city : Name of the city
        units : Metric/Imperial
        data : Weather data JSON
    """
    query = "INSERT INTO weather_data (city, units, data) VALUES (%s, %s, %s)"
    execute_query(config, 'WeatherDatabase', query, (city, units, json.dumps(data)))

def fetch_weather_from_db(config, city, units):
    """Fetch weather data from the database

    Args:
        config : Configuration settings from config.json
        city : Name of the city
        units : Metric/Imperial

    Returns:
        result : Weather data JSON
    """
    query = "SELECT data FROM weather_data WHERE city = %s AND units = %s ORDER BY created_at DESC LIMIT 1"
    result = execute_query(config, 'WeatherDatabase', query, (city, units), fetch_one=True)
    return json.loads(result['data']) if result else None