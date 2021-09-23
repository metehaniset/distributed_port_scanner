import sys
import ipaddress
import uuid
import re
from lib.logger import logger
from lib.queue_handler import QueueHandler
import time


class ScanManager:
    """
    Flask web app uses this class for pushing scan orders to rabbitmq
    """
    def __init__(self):
        # prepare queue
        self.queue = QueueHandler(host='rabbitmq')
        self.queue.bind(queue_name='distscanner_order', routing_key='work_order')

    def _check_port_string(self, port_string):
        # a little format checking for port string
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

    def send_to_scanners(self, scanner='ugly', host_string='127.0.0.1', port_string='1000-2000', params_string=None):
        if not self._check_port_string(port_string):
            return None

        scan_id = str(uuid.uuid4())
        try:
            host_list = ipaddress.IPv4Network(host_string)
        except:
            return None

        work = []
        ip_count = 0
        message = {'type': 'work_order', 'scanner': scanner, 'scan_id': scan_id}
        for ip in host_list:
            if str(ip).split('.')[3] in ['0', '255']:   # Dont scan broadcast adresess?
                continue
            ip_count += 1
            work.append({'host': str(ip), 'port_string': port_string, 'params': params_string})
            if len(work) == 8:    # split it, 8 host per work
                message['data'] = work
                self.queue.publish('work_order', message)
                work = []

        # push remaining work to queue
        if len(work) > 0:
            message['data'] = work
            self.queue.publish('work_order', message)
            # print(message)

        return {'scan_id': scan_id, 'ip_count': ip_count}

# # for testing
# def main():
#     time.sleep(30)
#     sm = ScanManager()
#     sm.send_to_scanners(host_string='192.168.1.0/24', port_string='2379')
#
#
# if __name__ == "__main__": main()
#
#
