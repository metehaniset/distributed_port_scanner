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
    def __init__(self):
        # prepare queue
        self.queue = QueueHandler(host='rabbitmq')
        self.elastic = Elasticsearch([{'host': 'elasticsearch', 'port': 9200}])

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
                self.update_db_with_result(scan_id, work_order_result)
                # self.process_result(message)
            else:
                logger.warning('Unknown message_type:', message['type'])
        except Exception as e:
            logger.exception('exception in execute_order callback')

    def update_db_with_result(self, scan_id, work_order_result):
        for r in work_order_result:
            r['geolocation'] = self.get_geolocation(r)
            r['scan_id'] = scan_id
            print('inserted', r)
            self.elastic.index(index="distscanner-result", body=r)
        pass

    # def update_db_with_result(self, scan_id, result):
    #     scan_id = "27b638ed-8e4c-4806-88e3-a06cdf5c7cb9"
    #     result = [{'host': '192.168.1.96', 'open_ports': [{'port': 5672, 'protocol': 'tcp', 'reason': 'syn-ack', 'service': {'name': 'unknown', 'version': 'unknown', 'os-type': 'unknown'}}]}, {'host': '192.168.1.97', 'open_ports': []}, {'host': '192.168.1.98', 'open_ports': []}, {'host': '192.168.1.99', 'open_ports': []}, {'host': '192.168.1.100', 'open_ports': []}, {'host': '192.168.1.101', 'open_ports': []}, {'host': '192.168.1.102', 'open_ports': []}, {'host': '192.168.1.103', 'open_ports': []}]
    #
    #     # res = es.search(index="distscanner-result", body={"query": {"match_all": {}}})
    #     res = self.elastic.search(index="distscanner-result", body={"query": {"match": {'scan_id':'27b638ed-8e4c-4806-88e3-a06cdf5c7cb9'}}})
    #     print("Got %d Hits:" % res['hits']['total']['value'])
    #     for hit in res['hits']['hits']:
    #         print(hit["_source"])
    #
    #     # for r in result:
    #     #     r['geolocation'] = self.get_geolocation(r)
    #     #     r['scan_id'] = scan_id
    #     #     self.elastic.index(index="distscanner-result", body=r)
    #
    #     return False

    def get_geolocation(self, result):
        return 'Turkey'


def main():
    # time.sleep(30)  # wait for rabbitmq
    sm = ResultManager()
    sm.run()


if __name__ == "__main__": main()
