# Aggregators

## Common choice for the aggregrators
1. **Structured Streaming:** Used PySpark Structured Stream to consume the data from kafka as a stream and write back to kafka as a stream. 

2. **Create a spark session:**
Make sure we use the right spark sql jars to run as structered stream, we are using spark-3.0.0 thus we need to use **spark-sql-kafka-0-10_2.12:3.0.0**
```
    session_object = SparkSession \
            .builder \
            .appName("PySpark Product Price Aggregration") \
            .master("local[*]") \
            .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.0.0") \
            .getOrCreate()
```
3. **Consume from Kafka as read stream**
We run this aggregrator as streaming process thus we use the startingOffsets as "latest"
```
    raw_data_df = pyspark_session \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
            .option("subscribe", KAFKA_RAW_DATA_TOPIC) \
            .option("startingOffsets", "latest") \
            .load()

```
## Aggregate Product Price by Order ID
The aggregration used here is to compute sum of product price grouped by order_id.

```
+-----------------------------------------------------------------------------------------------+
|value                                                                                          |
+-----------------------------------------------------------------------------------------------+
|{"time":"2020-06-30T05:57:15.117572", "order_id": "11106", "total_amount": "9295.4"}           |
|{"time":"2020-06-30T05:57:15.117572", "order_id": "11103", "total_amount": "6351.1"}           |
|{"time":"2020-06-30T05:57:15.117572", "order_id": "11111", "total_amount": "2229.5"}           |
|{"time":"2020-06-30T05:57:15.117572", "order_id": "11105", "total_amount": "8578.300000000001"}|
|{"time":"2020-06-30T05:57:15.117572", "order_id": "11108", "total_amount": "12976.0"}          |
|{"time":"2020-06-30T05:57:15.117572", "order_id": "11107", "total_amount": "6865.0"}           |
|{"time":"2020-06-30T05:57:15.117572", "order_id": "11110", "total_amount": "1493.9"}           |
|{"time":"2020-06-30T05:57:15.117572", "order_id": "11101", "total_amount": "14678.2"}          |
|{"time":"2020-06-30T05:57:15.117572", "order_id": "11104", "total_amount": "8386.1"}           |
|{"time":"2020-06-30T05:57:15.117572", "order_id": "11102", "total_amount": "7873.500000000001"}|
|{"time":"2020-06-30T05:57:15.117572", "order_id": "11109", "total_amount": "13028.6"}          |
|{"time":"2020-06-30T05:57:15.117572", "order_id": "11100", "total_amount": "12356.1"}          |
+-----------------------------------------------------------------------------------------------+

```

## Aggregate to_location by Product ID
The aggregration used here is to compute count of produts grouped to_location.

### DataFrame Before Aggregration
```
+----------+-----------+
|product_id|to_location|
+----------+-----------+
|1271      |92         |
|1025      |98         |
|1441      |54         |
|1042      |94         |
|1395      |95         |
|1209      |91         |
|1460      |69         |
|1090      |83         |
|1353      |98         |
|1375      |67         |
|1144      |84         |
|1329      |75         |
|1385      |89         |
|1343      |68         |
|1173      |89         |
|1363      |85         |
|1340      |91         |
|1453      |66         |
+----------+-----------+
```
### DataFrame After Aggregration
```
-------------------------------------------
Batch: 1
-------------------------------------------
+-----------+-------------+
|to_location|total_product|
+-----------+-------------+
|85         |1            |
|91         |2            |
|94         |1            |
|54         |1            |
|92         |1            |
|84         |1            |
|69         |1            |
|95         |1            |
|98         |2            |
|75         |1            |
|83         |1            |
|68         |1            |
|66         |1            |
|67         |1            |
|89         |2            |
+-----------+-------------+

```

