## Check order status
### Usage
```
$ python3 check_order_status.py
{'_id': ObjectId('5efa992c2079b7d5c5f75f80'), 'order_id': 11104, 'status': 'routed'}
{'_id': ObjectId('5efa992c2079b7d5c5f75f81'), 'order_id': 11105, 'status': 'routed'}
{'_id': ObjectId('5efa992c2079b7d5c5f75f82'), 'order_id': 11106, 'status': 'routed'}
{'_id': ObjectId('5efa9c2ccbe5893a970aa27f'), 'order_id': 11107, 'status': 'generated'}

$ python3 check_order_status.py -i 11108
order_id: 11108 status is routed
```
## Random IP generator
###  Usage
```
$ python3 generate_random_ip.py
{"ip_address":"238.22.187.86"}
{"ip_address":"45.65.84.172"}
{"ip_address":"141.7.150.86"}
....
....

$ python3 generate_random_ip.py >> fraud_ip.json
```
## Random Product Details generator
### Usage
```
$ python3 random_product_generator.py
{'product_id': 1496, 'product_name': 'hilly-viridian-antelope', 'route_id': 2, 'category': 'Baby'}
{'product_id': 1497, 'product_name': 'crabby-amethyst-zebu', 'route_id': 1, 'category': 'Young Adults'}
{'product_id': 1498, 'product_name': 'sunny-orange-zebra', 'route_id': 1, 'category': 'Shoes'}
....
....

$ python3 random_product_generator.py >> product_details.json
````
