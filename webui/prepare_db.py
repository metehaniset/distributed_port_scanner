from app import db
from app.models import User, Scan
from datetime import datetime
import random
import elasticsearch
from elasticsearch import Elasticsearch, exceptions
from lib.logger import logger
import time
from lib.utils import is_elastic_running

import logging
logging.getLogger("elasticsearch").setLevel(logging.WARNING)
"""
# flask db init
# flask db migrate -m "users table"
# flask db upgrade
"""

def generate_test_data(scan_id='9666b652-d082-4d72-b26b-2c98fd696499'):
    while True:
        try:
            elastic = Elasticsearch([{'host': 'elasticsearch', 'port': 9200}])

            if not is_elastic_running():
                logger.info('Elasticsearch is not ready')
                time.sleep(10)
                continue

            if elastic.indices.exists(index="distscanner-result"):
                # logger.info('distscanner-result index already exist on elasticsearch. Not running generate_test_data')
                return False

            logger.info('inserting test scan results to elasticsearch')
            for i in range(1, 255):
                if random.random() < 0.70:  # %70 probability for open ports
                    randoms = random.sample(range(1, 65534), 10)
                    tops = random.sample([21, 22, 135, 445, 80, 443, 8080, 8443, 123, 9200, 9300], 3)
                    open_ports = tops + randoms
                else:
                    open_ports = []

                host = {
                    'host': '192.168.1.'+str(i), 'params': None,
                    'open_ports': [],
                    'hostname': 'not implemented', 'geolocation': 'not implemented',
                    'completed_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3], 'scan_id': scan_id
                }
                for port in open_ports:
                    host['open_ports'].append(
                        {'port': port, 'protocol': 'tcp', 'reason': 'syn-ack',
                         'service': {'name': 'unknown', 'version': 'unknown', 'os-type': 'unknown'}}
                    )

                elastic.index(index="distscanner-result", body=host)

            logger.info('Test data inserted to elasticsearch')
            # break after inserting to elasticsearch
            break

        except Exception as e:
            time.sleep(10)
            logger.info('exception in startup script', e)
            continue

    return True


# logger.info('preparing admin user')
# u = User(username='admin', email='admin@localhost')
# u.set_password('admin')
# db.session.add(u)
# db.session.commit()
#
# logger.info('inserting test scan')

# scan_id = '9666b652-d082-4d72-b26b-2c98fd696499'
# u = User.query.get(1)
# s = Scan(
#     scan_id=scan_id, ip='192.168.1.0/24', port='0-65535', owner=u,
#     scanner='ugly', params='', ip_count=254, status='completed'
# )
# db.session.add(s)
# db.session.commit()

if __name__ == "__main__":
    generate_test_data()
