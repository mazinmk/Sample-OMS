# Generate Orders workflow
This Program has following functions:
1. **Generate random orders:** 
Orders are randomly generated using pythn random() and shuffle() method. Each order comprises of multiple products which is also randomly picked between 1-4 numbers. All the values for properties of the orders are also randomly generated.
```
  {'order_id': 11100, 'time': '2020-06-29T02:38:55.166689', 'ip_address': '128.69.191.226',
     'products': [
        {'product_id': 1001, 'order_qty': 1, 'from_location': 49, 'to_location': 98, 'unit_of_measures': 5, 'uom_type': 'M', 'product_price': 165.4},
        {'product_id': 1448, 'order_qty': 3, 'from_location': 27, 'to_location': 64, 'unit_of_measures': 2, 'uom_type': 'E', 'product_price': 692.2},
    ]
  }
```
2. **Transformation of data from nested to flatten structure**
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

3. **Publish the message tranformed data onto kafka**
The transformed data is published onto kafka producer using **json serialiser** in async mode, thus the module kafka_connect() does not have a feedback loop configured in kafka producer.

4. **Update the order status**
Once the message is published we need to update the order status as **generated**. The objective of maintaing the status is to enable status report tracking for each orders.
