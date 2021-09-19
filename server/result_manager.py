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
                scan_id = message['scan_id']
                logger.debug('New work_result captured')
                self.process_result(scan_id, work_order_result)
            else:
                logger.warning('Unknown message_type:', message['type'])
        except Exception as e:
            logger.exception('exception in execute_order callback')

    def process_result(self, scan_id, work_order_result):
        print(scan_id, work_order_result)
        pass

    def update_db_with_result(self):
        pass


sm = ResultManager()
sm.run()

