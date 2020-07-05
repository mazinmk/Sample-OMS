from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
from logger.applogger import *
from mymongo.mongo_connect import MyMongoDb
from mykafka.kafka_connect import MyKafkaConnect
from datetime import datetime
from json import dumps
import time
import sys
import random
import socket
import struct

RAW_TOPIC = "new_raw_orders"
LOGS_FILE = "logs/generateorder.log"

def update_order_status(order_list):
    """
    For each order which is published onto topic need to update the status of the topic
    onto "generated" in mondo db status collection.

    :input: list of published orders
    :output: None
    """
    try:
        #Acces the Monda Connection Object
        order_status_col = MyMongoDb.db.order_status
        for order_id in order_list:
            status_dict = {}
            status_dict["order_id"] = order_id
            status_dict["status"] = "generated"

            # Set the status in the status metastore
            result = order_status_col.insert_one(status_dict)
        logger.info("Orders Status changed to Generated successfully.")
    except Exception as ex_err:
        logger.error(f"Exception while Updating the status in mongo:{ex_err}")
        sys.exit(1)

def publish_data_to_kafka(flatten_data):
    """
    Publish the flattened data onto kafka topic where each order in the list will beinserted as one record.

    :input: List of Orders in flat structure
    :output: None
    """
    list_order_ids = []
    try:
        logger.info("Kafka Producer Application Started ... ")

        # Get the kafka producer object 
        kafka_connect_obj = MyKafkaConnect()
        kafka_producer = kafka_connect_obj.get_kafka_producer()

        # Publish the data onto kafka
        for each_record in flatten_data:
            list_order_ids.append(each_record["order_id"])
            kafka_producer.send(RAW_TOPIC, each_record)
        unique_order_set = set(list_order_ids)
        unique_order_list = list(unique_order_set)
        logger.info("Raw orders published successfully.")

        # Update the status of the order
        update_order_status(unique_order_list)
    except Exception as ex:
        logger.error(f"Exception in publishing message :{ex}")
        sys.exit(1)

def flatten(data):
    """
    Transform the nested structure of orders into flat structure.
    Structure of trasformed data is as follows
    { "product_id": 1215, "order_qty": 6, "from_location": 43, "to_location": 80, "unit_of_measures": 2,
      "uom_type": "E", "product_price": 1208.5, "order_id": 11103, "time": "2020-06-29T02:38:55.166689",
      "ip_address": "150.50.115.62"
    }

    :input: List of Orders in nested structure
    :output: List of Order in flat structure

    """
    list_flatten_data = []

    # Although there is nested for loop which might give an illusion that from Big-O 
    # notation which is N^3 time complexity which is not true in this as case.
    # Time complexity of this is O(n) as we are traversing through dictionary.
    for order in data:
        for product in order["products"]:
            for key in order.keys():
                if key != "products":
                    product[key] = order[key]
            list_flatten_data.append(product)
    return list_flatten_data

def generate_orders():
    """
    - Function to generate random orders which is nested structure and store these orders in list.
    - Orders are generated in batch mod generated in batch mode
    Structure of order generated is as follows.

    {'order_id': 11109, 'time': '2020-06-29T02:38:55.166689', 'ip_address': '63.166.108.212', 
     'products': [
     {'product_id': 1385, 'order_qty': 2, 'from_location': 49, 'to_location': 81, 'unit_of_measures': 8, 'uom_type': 'E', 'product_price': 4761.6}, 
     {'product_id': 1082, 'order_qty': 4, 'from_location': 26, 'to_location': 60, 'unit_of_measures': 7, 'uom_type': 'F', 'product_price': 3045.4}, 
     {'product_id': 1308, 'order_qty': 8, 'from_location': 16, 'to_location': 80, 'unit_of_measures': 12, 'uom_type': 'F', 'product_price': 1324.9}
    ]}

    :input: none
    :output: List of dictionaries of order
    """
    event_datetime = datetime.now().isoformat()
    arr_orders = []
    order_id = list(range(11100,11110))
    random.shuffle(order_id)
    uom_type_list = ["E", "M", "F"]
    for order in order_id:
        dict_products = {}
        list_products = []
        dict_products['order_id'] = order
        dict_products['time'] =  event_datetime

        # Generate random IP Address
        random_ip = socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))
        dict_products['ip_address'] = random_ip

        # Choose randomly for each order how many products you want to chose
        # Range from 1-4

        no_of_products = round(random.uniform(1,4))

        for products in range(no_of_products):
            dict_prod_details = {}
            dict_prod_details['product_id'] = round(random.uniform(1000,1500))
            dict_prod_details['order_qty'] = round(random.uniform(1,10))
            dict_prod_details['from_location'] = round(random.uniform(10,50))
            dict_prod_details['to_location'] = round(random.uniform(50,99))
            dict_prod_details['unit_of_measures'] = round(random.uniform(1,15))
            dict_prod_details['uom_type'] = random.choice(uom_type_list)
            dict_prod_details['product_price'] = round(random.uniform(10,5000),1)
            list_products.append(dict_prod_details)
        
        dict_products["products"] = list_products
        arr_orders.append(dict_products)
    return arr_orders


def main():

    #Generation random orders
    print("Generating Random orders .....")
    list_orders = generate_orders()
    
    # Transform the data from nested structure to flat structure
    logger.info("Flattening the data to 2D ...")
    flattened_data = flatten(list_orders)
    #print (dumps(flattened_data, indent=2))

    #Publoish
    publish_data_to_kafka(flattened_data)
    print("Order Generated")

if __name__ == "__main__":

    #Initialize logger to log all signals
    logger = configure_app_logger(__name__,LOGS_FILE)
    main()


