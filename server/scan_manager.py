import sys
import ipaddress
import uuid
import re
from lib.logger import logger
from lib.queue_handler import QueueHandler


class ScanManager:
    def __init__(self):
        # prepare queue
        self.queue = QueueHandler(host='rabbitmq')
        self.queue.bind(queue_name='distscanner_order', routing_key='work_order')

    def _check_port_string(self, port_string):
        # a little format checking
        if '-' in port_string:
            port_list = port_string.split('-')
            if len(port_list) > 2:
                return False
        elif ',' in port_string:
            port_list = port_string.split(',')
        else:   # numeric ?
            port_list = [port_string]

        for port in port_list:
            try:
                p = int(port)
                if p > 65535 or p < 0:
                    return False
            except:
                return False
        return True

    def send_to_scanners(self, host_string='127.0.0.1', port_string='1000-2000'):
        if not self._check_port_string(port_string):
            return None

        work_id = str(uuid.uuid4())
        host_list = ipaddress.IPv4Network(host_string)
        work = []
        work_count = 0
        for ip in host_list:
            work.append({'host': str(ip), 'port_string': port_string})
            if len(work) == 8:    # split it 8 host per work
                message = {'type': 'work_order', 'work_id': work_id, 'data': work}
                self.queue.publish('work_order', message)
                work = []
                work_count += 1

        # push remaining work to queue
        if len(work) > 0:
            message = {'type': 'work_order', 'work_id': work_id, 'data': work}
            self.queue.publish('work_order', message)
            work_count += 1

        return {'work_id': work_id, 'work_count': work_count}

    def get_results(self):
        pass

    def update_db_with_result(self):
        pass


# sm = ScanManager()
# sm.send_to_scanners(host_string='192.168.1.0/24', port_string='2379')
