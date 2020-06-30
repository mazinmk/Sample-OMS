from logger.applogger import *
from kafka import KafkaProducer, KafkaConsumer
from json import dumps, loads

"""
Consumer:
1. Kafka consumer is configured to consume from "latest" offset as this program will be running in
   stream mode.
2. Topics are created with single partition, but consumer group is configured to enable
   parallel process where more consumers can be added if needed to scale.
3.Auto Commit is set to true which means offset commit will happen every 5 sec.

Producer:
1. Messages are published onto kafka topic in async manner. Thus we dont wait for the feedback.

"""


_bootstrap_servers = "10.0.0.6:9092"
class my_kafka_connect(object):
    def __init__(self):
        pass

    def get_kafka_producer(self):
        kafka_producer_obj = None
        try:
            kafka_producer_obj = KafkaProducer(bootstrap_servers=_bootstrap_servers,
                                       value_serializer=lambda x: dumps(x).encode('utf-8'))
        except Exception as conn_err:
            logger.error(f"Exception while connecting to kafka:{conn_err}")
            sys.exit(1)
        finally:
            return kafka_producer_obj

    def get_kafka_consumer(self,topic_name,group_id,offset_reset):
        kafka_consumer_obj = None
        try:
            kafka_consumer_obj = KafkaConsumer(topic_name,
                                        bootstrap_servers=_bootstrap_servers,
                                        auto_offset_reset=offset_reset,
                                        enable_auto_commit=True,
                                        consumer_timeout_ms=1000,
                                        group_id=group_id,
                                        value_deserializer=lambda x: loads(x.decode('utf-8')))
        except Exception as ex:
            logger.error(f"Exception while connecting to kafka:{ex}")
            sys.exit(1)
        finally:
            return kafka_consumer_obj

