from mymongo.mongo_connect import my_mongo_db
from mykafka.kafka_connect import my_kafka_connect
from kafka.errors import KafkaError
from json import dumps, loads
from kafka import KafkaProducer, KafkaConsumer
#from pyspark.sql import SparkSession, Row
from logger.applogger import *
import time
import sys


KAFKA_VALID_ORDERS = "valid_orders"
KAFKA_LOCATION_ENRICHED = "enriched_order_details"
KAFKA_BOOTSTRAP_SERVERS = '10.0.0.6:9092'
LOG_FILE_NAME = "logs/enrich_order_location.log"

def get_name_for_location(location_object,location_id):
    """
    For a given location id look up the metastore to get the location name.

    :input: Mongo DB colletion object, location ID
    :output: Location Name
    """
    location_name = None
    for x in location_object.find({"location_id":location_id}):
        location_name = x["name"]
        return location_name

def enrich_message():
    """
    1.Enrich the data looking up at location_details metastore collections in mongo db
    2.Update the order status to "enriched" after publishing the data
    3.Run in a while loop to make it run as streaming process.

    :input: None
    :output: None
    """
    #Access the Mongo Connection Object
    location_collection =  my_mongo_db.db.location_details
    order_id_status_collection =  my_mongo_db.db.order_status

    #Create kafka producer and consumer object
    kafka_connect_obj = my_kafka_connect()
    kafka_producer = kafka_connect_obj.get_kafka_producer()
    kafka_consumer = kafka_connect_obj.get_kafka_consumer(KAFKA_VALID_ORDERS,
                                                          'enhanced_group',
                                                          'latest')
    try:
        while True:
            for message in kafka_consumer:
                status_dict={}
                order = message.value
                status_dict["order_id"] = order["order_id"]
                order["to_location_name"] = get_name_for_location(location_collection,order["to_location"])
                order["from_location_name"] = get_name_for_location(location_collection,order["from_location"])

                #Publish the data onto kafka
                kafka_producer.send(KAFKA_LOCATION_ENRICHED, order)
                logger.info("Enriched Order published successfully")

                #Update the order status
                order_id_status_collection.update_one(status_dict,{"$set":{"status":"enriched"}})
                logger.info("Order status changed from generated to validated.")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Keyboard CTRL-C interrupted!")
        sys.exit(0)
    except Exception as ex:
        logger.warning(f"Exception in consumimg message :{ex}")
        sys.exit(1)

def main():
    """
    1. Once the orders are validated,this program consumes the message from valid_orders topic 
    and enriches the data with respective location names for to_location and from_location filed 
    by looking up location details metadata stored in the MongoDB. Enriched data is then published
    onto enriched data stream.
    2. For the valid records the status of the order is updated from "generated" to "validated"

    :input: None
    :output: None

    """
    enrich_message()

if __name__ == "__main__":
    logger = configure_app_logger(__name__,LOG_FILE_NAME)
    logger.info("Log initiliazed successfully.")
    main()

