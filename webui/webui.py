from app import app
from prepare_db import generate_test_data
from lib.logger import logger

if __name__ == "__main__":
    if generate_test_data():
        logger.info('Test data generated on elasticsearch for running first time')
    app.run(host='0.0.0.0')
