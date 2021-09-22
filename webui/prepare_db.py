from app import db
from app.models import User, Scan
from datetime import datetime
import random
from elasticsearch import Elasticsearch

"""
# flask db init
# flask db migrate -m "users table"
# flask db upgrade
"""

#
def generate_test_data(scan_id):
    elastic = Elasticsearch([{'host': 'elasticsearch', 'port': 9200}])

    for i in range(1, 254):
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
        print(host)
#


# u = User(username='admin', email='admin@localhost')
# u.set_password('admin')
# db.session.add(u)
# db.session.commit()
#
# scan_id = '9666b652-d082-4d72-b26b-2c98fd696499'
# u = User.query.get(1)
# s = Scan(
#     scan_id=scan_id, ip='192.168.1.0/24', port='0-65535', owner=u,
#     scanner='ugly', params='', ip_count=254, status='completed'
# )
# db.session.add(s)
# db.session.commit()


# # # generate_test_data(scan_id)
