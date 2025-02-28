import mysql.connector
import json

CONFIG_PATH = 'mysite/config.json'

def load_config():
    with open(CONFIG_PATH) as config_file:
        return json.load(config_file)

config = load_config()

def clear_weather_table(config):
    """
    Clears the weather_data table in the WeatherDatabase daily at midnight UTC.
    This prevents the DB-full approach from using outdated data.
    Timings controlled by PythonAnywhere.

    Args:
        config (dict) : Configuration settings from config.json
    """
    db_config = config['WeatherDatabase']
    connection = mysql.connector.connect(
        host=db_config['host'],
        database=db_config['database'],
        user=db_config['user'],
        password=db_config['password']
    )
    cursor = connection.cursor()
    cursor.execute("DELETE FROM weather_data")
    connection.commit()
    cursor.close()
    connection.close()

if __name__ == "__main__":
    clear_weather_table(config)
