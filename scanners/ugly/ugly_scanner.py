import socket
from datetime import datetime
from multiprocessing.pool import ThreadPool
import multiprocessing
from lib.logger import logger


class UglyScanner:
    """
    This class is used for connect scanning
    """
    def _parse_portstring(self, port_string):
        """
        Parses port strings
        format 100-200
        :param port_string: accepted formats: 100-200 or 80,443 or 80
        :return: integer port list
        """
        if '-' in port_string:
            plist = port_string.split('-')
            if len(plist) > 2:
                return None
            else:
                plist = list(range(int(plist[0]), int(plist[1])))

        elif ',' in port_string:
            plist = port_string.split(',')
        else:  # numeric ?
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
        """

        :param param: param['port_string'], param['host']
        :return: adds completed_timestamp and open_ports key to param
        """
        port_list = self._parse_portstring(param['port_string'])
        param['open_ports'] = []
        try:
            if param['host'].split('.')[3] in ['0', '255']:  # dont scan broadcast adresses
                return
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
        param['completed_timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        return param

    def scan(self, scan_id, work_order):
        if len(work_order) > 0:
            cpu_count = multiprocessing.cpu_count()
            thread_count = cpu_count if len(work_order) >= cpu_count else len(work_order)

            pool = ThreadPool(processes=thread_count)
            # pool = multiprocessing.Pool(processes=thread_count)
            result = pool.map(self._check_if_open, work_order)
            pool.close()
            pool.join()

            return {'type': 'work_order_result', 'scan_id': scan_id, 'data': result}

