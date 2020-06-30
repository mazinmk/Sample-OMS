from mymongo.mongo_connect import my_mongo_db
from mykafka.kafka_connect import my_kafka_connect
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
from json import dumps, loads
from logger.applogger import *
import time
import sys


KAFKA_ENRICHED_TOPIC = "enriched_order_details"
KAFKA_INTERNAL_ROUTE = "internal_routed_order"
KAFKA_EXTERNAL_ROUTE = "external_routed_order"
KAFKA_BOOTSTRAP_SERVERS = '10.0.0.6:9092'
LOG_FILE_NAME = "logs/route_order.log"

def get_route(product_object,product_id):
    """
    For a given product id look up the product metastore to get the route id.

    :input:  Mongo DB collection object, Product id
    :output: Route type
    """
    route = None
    for x in product_object.find({"product_id":product_id}):
        route = x["route_id"]
        return route

def route_message():

    """
    1.Consume the message from enriched topic and based on the route set for each product 
    routes the product to the respective channel.
    2.Update the order status to "routed" after publishing the data
    3.Run in a while loop to make it run as streaming process.

    :input: None
    :output: None
    """

    #Access the Mongo Connection Object
    products_collection =  my_mongo_db.db.product_details
    order_status_collection =  my_mongo_db.db.order_status

    #Create kafka producer  and consumer object
    kafka_connect_obj = my_kafka_connect()
    kafka_producer = kafka_connect_obj.get_kafka_producer()
    kafka_consumer = kafka_connect_obj.get_kafka_consumer(KAFKA_ENRICHED_TOPIC,
                                                          'route_group',
                                                          'latest')
    try:
        while True:
            for message in kafka_consumer:
                status_dict={}
                order = message.value
                status_dict["order_id"] = order["order_id"]
                route_id = get_route(products_collection,order["product_id"])
                if route_id == 1:
                    kafka_producer.send(KAFKA_INTERNAL_ROUTE, order)
                    logger.info("Order published to Internal Route successfully")
                else:
                    kafka_producer.send(KAFKA_EXTERNAL_ROUTE, order)
                order_status_collection.update_one(status_dict,{"$set":{"status":"routed"}})
                logger.info("Order status changed from generated to validated.")
    except KeyboardInterrupt:
        print("Keyboard CTRL-C interrupted!")
        sys.exit(0)
    except KafkaError as ex:
        logger.error(f"Exception in consumimg message :{ex}")
        sys.exit(1)

def main():
    """
    1.This program consumes the message from enriched topic and based on the route set for each product
    in the roder routes the orders to the respective channel.
    2.We have set only two routes which is internal and external.
    3.For the routed orders update the status as "routed" in status collection

    :input: None
    :output: None

    """
    route_message()

if __name__ == "__main__":
    logger = configure_app_logger(__name__,LOG_FILE_NAME)
    logger.info("Log initiliazed successfully.")
    main()

