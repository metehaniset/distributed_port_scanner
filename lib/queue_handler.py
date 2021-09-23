import json
import logging
import sys
import time
import pika
from lib.logger import logger

logging.getLogger("pika").setLevel(logging.CRITICAL)


class QueueHandler:
    """
    wrapper for pika
    """
    def __init__(self, exchange_name='distscanner', exchange_type='direct', host='rabbitmq'):
        self._params = pika.ConnectionParameters(
            host=host,
            # virtual_host=virtual_host,
            # credentials=pika.credentials.PlainCredentials(username, password)
        )

        self.exchange_name = exchange_name
        self.exchange_type = exchange_type
        self._conn = None
        self.channel = None

    def connect(self):
        if not self._conn or self._conn.is_closed:
            while True:
                try:
                    self._conn = pika.BlockingConnection(self._params)
                    break
                except:
                    # logger.info('RabbitMQ is not ready. Waiting 10seconds')
                    time.sleep(10)

            self.channel = self._conn.channel()
            self.channel.exchange_declare(exchange=self.exchange_name, exchange_type=self.exchange_type)

    def disconnect(self):
        try:
            self._conn.close()
        except pika.exceptions.ConnectionWrongStateError:
            logger.info('Connection already closed')

    def bind(self, queue_name=None, routing_key=None):
        self.connect()
        self.channel.queue_declare(queue_name, durable=True)
        self.channel.queue_bind(exchange=self.exchange_name, queue=queue_name, routing_key=routing_key)

    def listen(self, queue_name=None, routing_key=None, callback=None, auto_ack=True):
        self.bind(queue_name=queue_name, routing_key=routing_key)
        self.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=auto_ack)
        while True:     # try again if exception happens
            try:
                self.channel.start_consuming()
            except KeyboardInterrupt:
                self.channel.stop_consuming()
                self._conn.close()
                logger.debug('Rabbitmq listener exiting gracefully')
                sys.exit(0)
            except (pika.exceptions.StreamLostError,
                    pika.exceptions.ConnectionClosed,
                    pika.exceptions.ChannelClosed,
                    ConnectionResetError):
                logger.info('Connection Exception in queue_handler.listen. Sleeping and trying')
                time.sleep(2)
                continue
            except Exception as e:
                logger.exception('Exception while trying to listen', queue_name, routing_key)
                time.sleep(2)
                continue

    def publish(self, routing_key, message):
        while True:
            try:
                self.channel.basic_publish(
                    exchange=self.exchange_name, routing_key=routing_key, body=json.dumps(message),
                    properties=pika.BasicProperties(
                        delivery_mode=2,    # Make message persistent
                    )
                )
                return True
            except (pika.exceptions.StreamLostError,
                    pika.exceptions.ConnectionClosed,
                    pika.exceptions.ChannelClosed,
                    ConnectionResetError):
                time.sleep(1)
                logger.warning('RECONNECTION IN PUBLISH. routing_key:', routing_key)
                self.connect()
                continue
            except Exception as e:
                logger.error('before publish channel:', self.channel)
                logger.exception('Exception while trying to publish to routing_key:', routing_key, message)
                return False

            return False
