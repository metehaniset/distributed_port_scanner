import sys
import ipaddress
import time
import uuid
import re
import json
from lib.logger import logger
from lib.queue_handler import QueueHandler
from elasticsearch import Elasticsearch

import logging
logging.getLogger("elasticsearch").setLevel(logging.WARNING)


class ResultManager:
    """
    Takes scan results from queue, makes some enrichment and writes to elasticsearh
    """
    def __init__(self):
        # prepare queue
        self.queue = QueueHandler(host='rabbitmq')
        self.elastic = Elasticsearch([{'host': 'elasticsearch', 'port': 9200}])

    def run(self):
        self.queue.listen(queue_name='distscanner_result', routing_key='work_order_result', callback=self.work_order_listener, auto_ack=False)

    def work_order_listener(self, ch, method, properties, body):
        try:
            logger.debug('New work_result captured')
            message = json.loads(body)
            if message['type'] == 'heartbeat':
                # logger.info('heartbeat captured')
                pass
            elif message['type'] == 'work_order_result':
                work_order_result = message['data']
                scan_id = message['scan_id']
                self.update_db_with_result(scan_id, work_order_result)
                # self.process_result(message)
            else:
                logger.warning('Unknown message_type:', message['type'])
        except Exception as e:
            logger.exception('exception in execute_order callback')

        ch.basic_ack(delivery_tag=method.delivery_tag)  # send acknowledgment

    def update_db_with_result(self, scan_id, work_order_result):
        for r in work_order_result:
            self.improve_data(r)
            r['scan_id'] = scan_id
            # print('inserted', r)
            logger.info(r)
            self.elastic.index(index="distscanner-result", body=r)

    def improve_data(self, host):
        self.get_geolocation(host)
        self.get_hostname(host)

    def get_geolocation(self, result):
        return 'not implemented'

    def get_hostname(self, result):
        return 'not implemented'


def main():
    # time.sleep(30)  # wait for rabbitmq
    sm = ResultManager()
    sm.run()


if __name__ == "__main__": main()
