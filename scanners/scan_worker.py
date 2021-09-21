from lib.queue_handler import QueueHandler
from lib.logger import logger
from scanners.ugly.ugly_scanner import UglyScanner
from scanners.nmap.nmap_manager import NmapManager
from scanners.nessus.nessus_manager import NessusManager
from scanners.arachni.arachni_manager import ArachniManager
import json
import time


class ScanWorker:
    def __init__(self):
        self.queue = QueueHandler()

    def run(self):
        self.queue.bind(queue_name='distscanner_result', routing_key='work_order_result')
        self.queue.listen(queue_name='distscanner_order', routing_key='work_order', callback=self.work_listener, auto_ack=False)

    def work_listener(self, ch, method, properties, body):
        try:
            message = json.loads(body)
            if message['type'] == 'heartbeat':
                # logger.info('heartbeat captured')
                pass
            elif message['type'] == 'work_order':
                if message['scanner'] == 'ugly':
                    scanner = UglyScanner()
                elif message['scanner'] == 'nmap':
                    scanner = NmapManager()
                elif message['scanner'] == 'nessus':
                    scanner = NessusManager()
                elif message['scanner'] == 'arachni':
                    scanner = ArachniManager()
                else:
                    logger.critical("Unknown scanner:", message['scanner'])
                    ch.basic_ack(delivery_tag=method.delivery_tag)  # send acknowledgment or maybe not?
                    return

                message = scanner.scan(message['scan_id'], message['data'])
                self.queue.publish('work_order_result', message)
        except Exception as e:
            logger.exception('exception in execute_order callback', e)

        ch.basic_ack(delivery_tag=method.delivery_tag)  # send acknowledgment


def main():
    # time.sleep(30)  # wait for rabbitmq
    sm = ScanWorker()
    sm.run()


if __name__ == "__main__": main()
