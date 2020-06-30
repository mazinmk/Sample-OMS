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

## Aggregate to_location by Product ID
The aggregration used here is to compute count of produts grouped to_location.


