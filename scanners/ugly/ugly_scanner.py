import sys
import socket
from datetime import datetime
from multiprocessing.pool import ThreadPool
import multiprocessing
from lib.queue_handler import QueueHandler
from lib.logger import logger
import json


class UglyScanner:
    def __init__(self):
        self.queue = QueueHandler()

    def run(self):
        self.queue.listen(queue_name='distscanner_order', routing_key='work_order', callback=self.work_listener)
        self.queue.bind(queue_name='distscanner_result', routing_key='work_order_result')

    def _parse_portstring(self, port_string):
        if '-' in port_string:
            plist = port_string.split('-')
            if len(plist) > 2:
                return None
            else:
                plist = list(range(int(plist[0]), int(plist[1])))

        elif ',' in port_string:
            plist = port_string.split(',')
        else:   # numeric ?
            plist = [port_string]

        port_list = []
        for port in plist:
            try:
                p = int(port)
                if p > 65535 or p < 0:
                    return None
                else:
                    port_list.append(p)
            except:
                return None

        return port_list

    def _check_if_open(self, param):
        port_list = self._parse_portstring(param['port_string'])
        param['open_ports'] = []
        try:
            for port in port_list:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                socket.setdefaulttimeout(1)
                result = s.connect_ex((param['host'], port))
                if result == 0:
                    param['open_ports'].append({
                        'port': port, 'protocol': 'tcp', 'reason': 'syn-ack',
                        'service': {
                            'name': 'unknown',
                            'version': 'unknown',
                            'os-type': 'unknown',
                        }
                        # bla bla...
                    })
                s.close()
        except Exception as e:
            logger.exception('Exception in _check_if_open', e)
            pass

        del param['port_string']
        return param

    def work_listener(self, ch, method, properties, body):
        try:
            message = json.loads(body)
            if message['type'] == 'heartbeat':
                # logger.info('heartbeat captured')
                return
            elif message['type'] == 'work_order':
                work_order = message['data']
                work_id = message['work_id']
                logger.debug('New work accepted')
                self.scan(work_id, work_order)
        except Exception as e:
            logger.exception('exception in execute_order callback')

    def scan(self, work_id, work_order):
        if len(work_order) > 0:
            cpu_count = multiprocessing.cpu_count()
            thread_count = cpu_count if len(work_order) >= cpu_count else len(work_order)

            pool = ThreadPool(processes=thread_count)
            result = pool.map(self._check_if_open, work_order)
            pool.close()
            pool.join()

            message = {'type': 'work_order_result', 'work_id': work_id, 'data': result}
            # print(message)
            self.queue.publish('work_order_result', message)


us = UglyScanner()
us.run()




"""
   <port protocol="tcp" portid="22">
    <state state="open" reason="syn-ack" reason_ttl="53"/>
    <service name="ssh" product="OpenSSH" version="5.3p1 Debian 3ubuntu7"
             extrainfo="protocol 2.0" ostype="Linux" method="probed" conf="10">
     <cpe>cpe:/a:openbsd:openssh:5.3p1</cpe>
     <cpe>cpe:/o:linux:kernel</cpe>
    </service>
    <script id="ssh-hostkey"
            output="1024 8d:60:f1:7c:ca:b7:3d:0a:d6:67:54:9d:69:d9:b9:dd (DSA)&#xa;
                    2048 79:f8:09:ac:d4:e2:32:42:10:49:d3:bd:20:82:85:ec (RSA)"/>
   </port>
   
"""