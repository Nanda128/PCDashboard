from flask import Flask
from logger import LoggerManager

logger = LoggerManager().get_logger()

app = Flask(__name__)

@app.route('/')
def index():
    return "Welcome to the Flask Web Application!"

if __name__ == '__main__':
    logger.info('Web App successfully started!')
    app.run(debug=True)