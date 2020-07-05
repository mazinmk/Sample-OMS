from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
from mymongo.mongo_connect import MyMongoDb
from mykafka.kafka_connect import MyKafkaConnect
from logger.applogger import *
from json import dumps, loads
import sys
import time


RAW_TOPIC = "new_raw_orders"
VALID_ORDERS = "valid_orders"
LOGS_FILE = "logs/validate_order.log"

def validate_orders():
    """
    1.Validate order for fraud_ip
    2.For the valid records the status of the order is updated from "generated" to "validated"
    3.Run in a while loop to make it run as streaming process.

    :input: None
    :output: None

    """
    #Create kafka producer and consumer object
    kafka_connect_obj = MyKafkaConnect()
    kafka_producer = kafka_connect_obj.get_kafka_producer()
    kafka_consumer = kafka_connect_obj.get_kafka_consumer(RAW_TOPIC,
                                                          'validate_group',
                                                          'latest')
    #Create Mongo Connection Object
    fraud_ip_collection = MyMongoDb.db.frauid_ip
    order_id_status_collection = MyMongoDb.db.order_status

    try:
        while True:
            for message in kafka_consumer:
                status_dict = {}
                ip_document_to_check ={}
                order = message.value
                ip_address = order["ip_address"]
                order_id = order["order_id"]
                ip_document_to_check["ip_address"] = ip_address
                status_dict["order_id"] = order_id

                # Check the fraud DB to see if the entry is there 
                if (fraud_ip_collection.find(ip_document_to_check).count()):
                    print ("This is fraud skip this record or entry into fraud stream")
                else:
                    kafka_producer.send(VALID_ORDERS, order)
                    logger.info("Enriched Raw Message published successfully.")
                    # Update the valid orders status in the order status collection
                    try:
                        order_id_status_collection.update_one(status_dict,{"$set":{"status":"validated"}})
                        logger.info("Order status changed from generated to validated.")
                    except Exception as ex:
                        logger.error(f"Exception in Updating status message in mongo db :{ex}")
                        sys.exit(1)
            time.sleep(1)
    except KeyboardInterrupt:
        print('Keyboard CTRL-C interrupted!')
        sys.exit(0)
    except KafkaError as kafka_err:
        logger.error(f"Exception in consumimg message :{kafka_err}")
        sys.exit(1)
    except Exception as ex:
        logger.warning(f"Exception has occured:{ex}")
        sys.exit(1)

def main():
    """
    Once the orders are generated in bacth mode, this program consumes the message from 
    raw_orders topic and each order is validated against the fradulent IP addressess 
    stored in fraud ip collection in mongo DB. Those orders which is valid will be published
    on to valid_orders stream.
    """
    validate_orders()

if __name__ == "__main__":

    #Initialize logger to log all signals
    logger = configure_app_logger(__name__,LOGS_FILE)
    logger.info("Log initiliazed successfully.")
    main()

