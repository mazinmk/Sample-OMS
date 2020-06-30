# Generate Orders workflow
This Program has following functions:
1. ***Generate random orders:*** 
Orders are randomly generated using pythn random() and shuffle() method. Each order comprises of multiple products which is also randomly picked between 1-4 numbers. All the values for properties of the orders are also randomly generated.
```
  {'order_id': 11100, 'time': '2020-06-29T02:38:55.166689', 'ip_address': '128.69.191.226',
     'products': [
        {'product_id': 1001, 'order_qty': 1, 'from_location': 49, 'to_location': 98, 'unit_of_measures': 5, 'uom_type': 'M', 'product_price': 165.4},
        {'product_id': 1448, 'order_qty': 3, 'from_location': 27, 'to_location': 64, 'unit_of_measures': 2, 'uom_type': 'E', 'product_price': 692.2},
    ]
  }
```
2. ***Transformation of data from nested to flatten structure:***
In order to process that data it is needed to flatten the datastructure from nested structure to flat structure so that this can be easily converted into dataframes for aggregation and otehr computation needed. In the above example, each order has 2 products thus post transformation one record will be tranformed into
flattened structure resulting in 2 records
```
[
  { "product_id": 1001,"order_qty": 1,"from_location": 49,"to_location": 98,"unit_of_measures": 5,"uom_type": "M",
     "product_price": 165.4,"order_id": 11100,"time": "2020-06-30T04:33:34.242637","ip_address": "128.69.191.226"
  },
  {
    "product_id": 1448,"order_qty": 3,"from_location": 27,"to_location": 64,"unit_of_measures": 2,"uom_type": "F",
    "product_price": 692.2,"order_id": 11100,"time": "2020-06-30T04:33:34.242637","ip_address": "128.69.191.226"
  },
```

3. ***Publish the message tranformed data onto kafka:***
The transformed data is published onto kafka producer using **json serialiser** in async mode, thus the module kafka_connect() does not have a feedback loop configured in kafka producer.

4. ***Update the order status:***
Once the message is published we need to update the order status as **generated**. The objective of maintaing the status is to enable status report tracking for each orders.
You can use **check_order_status.py** to check the status of all the orders.
```
$  python3 check_order_status.py
{'_id': ObjectId('5efac09e983fe22729abaabd'), 'order_id': 11100, 'status': 'generated'}
{'_id': ObjectId('5efac09e983fe22729abaabe'), 'order_id': 11101, 'status': 'generated'}
```

# Validate Orders workflow
This program has following functions:

1. ***Consume message from raw_order topic:***
    * Kafka consumer is configured to consume from "latest" offset as this program will be running in
   stream mode.
    * Topics are created with single partition, but consumer group "enhanced_group" is configured to enable 
   parallel process where more consumers can be added if needed to scale.
    * Auto Commit is set to true which means offset commit will happen every 5 sec.

2. ***Validate the order:***
Validation is set only to check against the fraudulent ipaddress which is populated onto fraud_ip metastore.For each record we extract ip address and valid against fraud_ip collection. If the IP address is not present in the ip_address collection the message is published onto **valid_orders** topic.

3. ***Publish the message tranformed data onto kafka:***
The validated order is published onto kafka producer using **json serialiser** in async mode, thus the module kafka_connect() does not have a feedback loop configured in kafka producer.

4. ***Update the order status:***
Once the message is published we need to update the order status as **validated**. The objective of maintaing the status is to enable status report tracking for each orders.
```
$  python3 check_order_status.py
{'_id': ObjectId('5efac09e983fe22729abaabd'), 'order_id': 11100, 'status': 'validated'}
{'_id': ObjectId('5efac09e983fe22729abaabe'), 'order_id': 11101, 'status': 'valdiated'}
```
# Enrich Data workflow
1. ***Consume message from valid_order topic:***
    * Kafka consumer is configured to consume from "latest" offset as this program will be running in
   stream mode.
    * Topics are created with single partition, but consumer group is configured to enable
   parallel process where more consumers can be added if needed to scale.
    * Auto Commit is set to true which means offset commit will happen every 5 sec.

2. ***Get the name of location based on location id :***
For a given location id look up the metastore to get the location name and return the location name using get_name_for_location().

3. ***Enrich orders:***
Enriches the data with respective location names for to_location and from_location field by looking up location details metadata stored using get_name_for_location()Enriched data is then published onto **enriched_order_details** topic.

4. ***Publish the message tranformed data onto kafka:***
The enhanced order is published onto kafka producer using **json serialiser** in async mode, thus the module kafka_connect() does not have a feedback loop configured in kafka producer.

5. ***Update the order status:***
Once the message is published we need to update the order status as **enriched**. The objective of maintaing the status is to enable status report tracking for each orders.
```
$  python3 check_order_status.py
{'_id': ObjectId('5efac09e983fe22729abaabd'), 'order_id': 11100, 'status': 'enriched'}
{'_id': ObjectId('5efac09e983fe22729abaabe'), 'order_id': 11101, 'status': 'enriched'}
```
# Route Data workflow
1. ***Consume message from enriched_order_details topic:***
    * Kafka consumer is configured to consume from "latest" offset as this program will be running in stream mode.
    * Topics are created with single partition, but consumer group "route_group" is configured to enable 
    parallel process where more consumers can be added if needed to scale.
    * Auto Commit is set to true which means offset commit will happen every 5 sec.

2. ***Get the route_id on product id*:**
For a given product id look up the product_details collection and get the route_id and return the id using get_route().

3. ***Route the order:***
There are only **two routes** configured today, which is, internal or external. Based on the route_id the orders are pusblished onto two different topics **internal_routed_order** or **external_routed_order**. Those topics which are set interally will follow internal order processing workflow and those order which are routed to external will be converted into json file and can be routed to external partners using API endpoints of clients.

4. ***Publish the message tranformed data onto kafka:***
The enhanced order is published onto kafka producer using **json serialiser** in async mode, thus the module kafka_connect() does not have a feedback loop configured in kafka producer.

5. ***Update the order status:***
Once the message is published we need to update the order status as **routed**. The objective of maintaing the status is to enable status report tracking for each orders.
```
$  python3 check_order_status.py
{'_id': ObjectId('5efac09e983fe22729abaabd'), 'order_id': 11100, 'status': 'routed'}
{'_id': ObjectId('5efac09e983fe22729abaabe'), 'order_id': 11101, 'status': 'routed'}
```


