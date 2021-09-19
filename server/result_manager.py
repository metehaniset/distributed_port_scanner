import sys
import ipaddress
import uuid
import re
import json
from lib.logger import logger
from lib.queue_handler import QueueHandler


class ResultManager:
    def __init__(self):
        # prepare queue
        self.queue = QueueHandler(host='rabbitmq')

    def run(self):
        self.queue.listen(queue_name='distscanner_result', routing_key='work_order_result', callback=self.work_order_listener)

    def work_order_listener(self, ch, method, properties, body):
        try:
            message = json.loads(body)
            if message['type'] == 'heartbeat':
                # logger.info('heartbeat captured')
                return
            elif message['type'] == 'work_order_result':
                work_order_result = message['data']
                work_id = message['work_id']
                logger.debug('New work_result captured')
                self.process_result(work_id, work_order_result)
            else:
                logger.warning('Unknown message_type:', message['type'])
        except Exception as e:
            logger.exception('exception in execute_order callback')

    def process_result(self, work_id, work_order_result):
        print(work_id, work_order_result)
        # 27b638ed-8e4c-4806-88e3-a06cdf5c7cb9 [{'host': '192.168.1.96', 'open_ports': [{'port': 5672, 'protocol': 'tcp', 'reason': 'syn-ack', 'service': {'name': 'unknown', 'version': 'unknown', 'os-type': 'unknown'}}]}, {'host': '192.168.1.97', 'open_ports': []}, {'host': '192.168.1.98', 'open_ports': []}, {'host': '192.168.1.99', 'open_ports': []}, {'host': '192.168.1.100', 'open_ports': []}, {'host': '192.168.1.101', 'open_ports': []}, {'host': '192.168.1.102', 'open_ports': []}, {'host': '192.168.1.103', 'open_ports': []}]
        pass

    def update_db_with_result(self):
        pass


sm = ResultManager()
sm.run()

