from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
from mymongo.mongo_connect import my_mongo_db
from mykafka.kafka_connect import my_kafka_connect
from logger.applogger import *
from json import dumps, loads, dump
import sys
import time
import os

EXTERNAL_ROUTE_TOPIC = "external_routed_order"
KAFKA_BOOTSTRAP_SERVERS = '10.0.0.6:9092'
LOG_FILE_NAME= "logs/external_order_process.log"
EXTERNAL_FOLDER = "external_orders"

def process_external_orders():
    """
    1.Validate order for fraud_ip
    2.For the valid records the status of the order is updated from "generated" to "validated"
    3.Run in a while loop to make it run as streaming process.

    :input: None
    :output: None

    """
    #Create kafka producer and consumer object
    kafka_connect_obj = my_kafka_connect()
    kafka_producer = kafka_connect_obj.get_kafka_producer()
    kafka_consumer = kafka_connect_obj.get_kafka_consumer(EXTERNAL_ROUTE_TOPIC,
                                                          'external_group',
                                                          'earliest')
    #Create Mongo Connection Object
    order_id_status_collection = my_mongo_db.db.order_status
    list_orders = []
    try:
        while True:
            for message in kafka_consumer:
                order_record_dict = message.value
                list_orders.append(order_record_dict)
                json_file_name = (EXTERNAL_FOLDER+"/"+str(order_record_dict["order_id"])+".json")
                try:
                    with open (json_file_name,'w') as external_order_json:
                        dump(list_orders, external_order_json)
                        logger.info (f"{json_file_name} JSON created for external orders")
                except IOError as ioerr:
                    logger.warning(f"Reading failed I/O {json_file_name} : {ioerr}")

    except KeyboardInterrupt:
        print('Keyboard CTRL-C interrupted!')
        sys.exit(0)
    except KafkaError as kafka_err:
        logger.error(f"Exception in consumimg message :{kafka_err}")
        sys.exit(1)
    except Exception as ex:
        logger.error(f"Exception has occured:{ex}")
        sys.exit(1)

def main():
    """
    All the external routed orders needs to converted into json so that it can be routed to 
    external using client API end point.
    """
    if not os.path.exists(EXTERNAL_FOLDER):
        os.makedirs(EXTERNAL_FOLDER)

    process_external_orders()

if __name__ == "__main__":

    #Initialize logger to log all signals
    logger = configure_app_logger(__name__,LOG_FILE_NAME)
    logger.info("Log initiliazed successfully.")
    main()

