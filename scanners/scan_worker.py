from lib.queue_handler import QueueHandler
from lib.logger import logger
from scanners.ugly.ugly_scanner import UglyScanner
from scanners.nmap.nmap_manager import NmapManager
from scanners.nessus.nessus_manager import NessusManager
from scanners.arachni.arachni_manager import ArachniManager
import json
import time


class ScanWorker:
    """
    takes work order from queue, chooses suitable scanner, starts scan and pushes results to queue
    """
    def __init__(self):
        self.queue = QueueHandler()

    def run(self):
        self.queue.bind(queue_name='distscanner_result', routing_key='work_order_result')   # pushing results
        self.queue.listen(queue_name='distscanner_order', routing_key='work_order',
                          callback=self.work_listener, auto_ack=False)    # listens for scan orders

    def work_listener(self, ch, method, properties, body):
        try:
            logger.debug('New scan request captured')
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
            else:
                logger.critical('Unknown message type:', message['type'])
        except Exception as e:
            logger.exception('exception in execute_order callback', e)

        ch.basic_ack(delivery_tag=method.delivery_tag)  # send acknowledgment


if __name__ == "__main__":
    sm = ScanWorker()
    sm.run()
