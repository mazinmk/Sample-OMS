from mymongo.mongo_connect import my_mongo_db
from datetime import datetime
import argparse
import sys


def main(order_id):
    """
    Check the status of the order in order_status collection.
    Default behaviour is to retrievethe status for all the orders,
    if you have choose -i <order_id> then it will retrieve the status 
    for that particular id
    """
    order_id_status_collection =  my_mongo_db.db.order_status
    if (order_id):
        for x in order_id_status_collection.find({"order_id":order_id}):
            order_status = x["status"]
            print (f"order_id: {order_id} status is {order_status}")
    else:
        for order_status in order_id_status_collection.find():
            print(order_status)

def check_arg(args=None):
    """
    Input: Order Id which shouldbe an integer type
   
    """
    parser = argparse.ArgumentParser(description="check_order_status - Program to check the status of the order",
                                    epilog="I hope you enjoy the program")
    parser.add_argument('-i', '--order_id',
                        type=int,
                        help="Provide order id if you know")
    results = parser.parse_args(args)
    return (results.order_id)

if __name__ == "__main__":
    
    """
        - Validate the command line inputs.
    """
    order_id = check_arg(sys.argv[1:])
    main(order_id)
