import sys
import ipaddress
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
                work_id = message['work_id']
                logger.debug('New work_result captured')
                self.update_db_with_result(work_id, work_order_result)
                # self.process_result(message)
            else:
                logger.warning('Unknown message_type:', message['type'])
        except Exception as e:
            logger.exception('exception in execute_order callback')

    def update_db_with_result(self, work_id, work_order_result):
        for r in work_order_result:
            r['geolocation'] = self.get_geolocation(r)
            r['work_id'] = work_id
            print('inserted', r)
            self.elastic.index(index="distscanner-result", body=r)
        pass

    # def update_db_with_result(self, work_id, result):
    #     work_id = "27b638ed-8e4c-4806-88e3-a06cdf5c7cb9"
    #     result = [{'host': '192.168.1.96', 'open_ports': [{'port': 5672, 'protocol': 'tcp', 'reason': 'syn-ack', 'service': {'name': 'unknown', 'version': 'unknown', 'os-type': 'unknown'}}]}, {'host': '192.168.1.97', 'open_ports': []}, {'host': '192.168.1.98', 'open_ports': []}, {'host': '192.168.1.99', 'open_ports': []}, {'host': '192.168.1.100', 'open_ports': []}, {'host': '192.168.1.101', 'open_ports': []}, {'host': '192.168.1.102', 'open_ports': []}, {'host': '192.168.1.103', 'open_ports': []}]
    #
    #     # res = es.search(index="distscanner-result", body={"query": {"match_all": {}}})
    #     res = self.elastic.search(index="distscanner-result", body={"query": {"match": {'work_id':'27b638ed-8e4c-4806-88e3-a06cdf5c7cb9'}}})
    #     print("Got %d Hits:" % res['hits']['total']['value'])
    #     for hit in res['hits']['hits']:
    #         print(hit["_source"])
    #
    #     # for r in result:
    #     #     r['geolocation'] = self.get_geolocation(r)
    #     #     r['work_id'] = work_id
    #     #     self.elastic.index(index="distscanner-result", body=r)
    #
    #     return False

    def get_geolocation(self, result):
        return 'Turkey'


sm = ResultManager()
# sm.elastic.indices.delete('my_index')
sm.run()
#
# work_id = '27b638ed-8e4c-4806-88e3-a06cdf5c7cb9'
#
#
# query = {"query": {"match": {'work_id': '27b638ed-8e4c-4806-88e3-a06cdf5c7cb9'}}}
# result = sm.elastic.search(index="distscanner-result", body=query)
# print(result)
#
