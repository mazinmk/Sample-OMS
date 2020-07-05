from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
from mymongo.mongo_connect import MyMongoDb
from mykafka.kafka_connect import MyKafkaConnect
from logger.applogger import *
from json import dumps, loads, dump
import sys
import time
import os

EXTERNAL_TOPIC = "external_routed_order"
LOGS_FILE= "logs/external_order_process.log"
EXTERNAL_FOLDER = "external_orders"

def process_orders():
    """

    :input: None
    :output: None

    """
    #Create kafka producer and consumer object
    kafka_connect_obj = MyKafkaConnect()
    kafka_producer = kafka_connect_obj.get_kafka_producer()
    kafka_consumer = kafka_connect_obj.get_kafka_consumer(EXTERNAL_TOPIC,
                                                          'external_group',
                                                          'earliest')
    #Create Mongo Connection Object
    order_id_status_collection = MyMongoDb.db.order_status

    list_orders = []
    try:
        while True:
            for message in kafka_consumer:
                status_dict = {}
                order_record_dict = message.value
                status_dict["order_id"] = order_record_dict["order_id"]
                list_orders.append(order_record_dict)
                json_file_name = (EXTERNAL_FOLDER+"/"+str(order_record_dict["order_id"])+".json")
                try:
                    with open (json_file_name,'w') as external_order_json:
                        dump(list_orders, external_order_json)
                    logger.info (f"{json_file_name} JSON created for external orders")
                    order_id_status_collection.update_one(status_dict,{"$set":{"status":"external_routed"}})
                    logger.info("Order status changed to external_routed.")
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

    process_orders()

if __name__ == "__main__":

    #Initialize logger to log all signals
    logger = configure_app_logger(__name__,LOGS_FILE)
    logger.info("Log initiliazed successfully.")
    main()

