from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from datetime import datetime


ENHANCED_ORDER = "enriched_order_details"
ORDER_PRICE = "order_price"
BOOTSTRAP_SERVER = '10.0.0.6:9092'



def get_pyspark_session():
    """
    Create spark session object.

    :input: None
    :output: Spark session object
    """
    session_object = SparkSession \
            .builder \
            .appName("PySpark Product Price Aggregration") \
            .master("local[*]") \
            .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.0.0") \
            .getOrCreate()

    return session_object

def spark_it_up():
    """
    1. Run a spark job to calculate sum of product prices aggregated by order id
    2. Consumes the data as kafka read stream from enriched topic loads the data 
    onto Dataframe where each message json object is loaded onto column.
    3. Transform the data untill we need columns what is needed to compute the sum
    of product price group by order id
    4. Publish the tranformed data onto kafka write stream
    5. This program is run as streaming process.
    """

    print("PySpark Structured Streaming Started ...")
    pyspark_session  = get_pyspark_session()

    pyspark_session.sparkContext.setLogLevel("ERROR")

    # Construct a streaming DataFrame that reads from testtopic
    raw_data_df = pyspark_session \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", BOOTSTRAP_SERVER) \
            .option("subscribe", ENHANCED_ORDER) \
            .option("startingOffsets", "latest") \
            .load()


    # Convert the key value from the message into string and timestamp
    transformation_df1 = raw_data_df.selectExpr("CAST(value AS STRING)", "timestamp")
    
    # Define a schema for the input raw data
    df_detail_schema = StructType() \
            .add("ip_address", StringType()) \
            .add("product_id", IntegerType()) \
            .add("order_qty", IntegerType()) \
            .add("from_location", IntegerType()) \
            .add("to_location", IntegerType()) \
            .add("unit_of_measures", IntegerType()) \
            .add("uom_type", StringType()) \
            .add("product_price", DoubleType()) \
            .add("order_id", IntegerType()) \
            .add("time", StringType())\
            .add("to_location_name", StringType())\
            .add("from_location_name", StringType())

    # Create an alias for the column which as the order message json object
    transformation_df2 = transformation_df1\
            .select(from_json(col("value"), df_detail_schema).alias("order_details"), "timestamp")

    # Convert the json object which is stored under value column onto multiple columns
    # based on the key name of the json object.
    transformation_df3 = transformation_df2.select("order_details.*", "timestamp")
    transformation_df3.printSchema()

    # From the key of the message chose only order_id product price and time column 
    # which is neede to compute the aggregated sum of product price
    transformation_df4 = transformation_df3.select("time","order_id","product_price")

    # Aggregate product_price by gorder id
    transformation_df5 = transformation_df4.groupBy("order_id")\
            .agg({'product_price': 'sum'}).select("order_id", \
            col("sum(product_price)").alias("total_amount"))


    # Trasform the new computed data on to json format
    transformation_df6 = transformation_df5.withColumn("time", lit(datetime.now().isoformat()))\
                                                   .withColumn("value", concat(
                                                       lit("{\"time\":\""), col("time"),
                                                       lit("\", \"order_id\": \""), col("order_id"), 
                                                       lit("\", \"total_amount\": \""),col("total_amount").cast("string"), 
                                                       lit("\"}")))

    # Select only the column which has the json object of computed values.
    transformation_df7 = transformation_df6.select("value")

    # Write final datafram result into console 
    final_df_write_console = transformation_df7 \
            .writeStream \
            .trigger(processingTime='1 seconds') \
            .outputMode("update") \
            .option("truncate", "false")\
            .format("console") \
            .start()

    #final_df_write_console.awaitTermination()

    #Write key-value data from a DataFrame to a specific Kafka topic specified in an option
    final_df_write_stream = transformation_df7 \
            .writeStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", BOOTSTRAP_SERVER) \
            .option("topic", ORDER_PRICE) \
            .trigger(processingTime='1 seconds') \
            .outputMode("update") \
            .option("checkpointLocation", "order_price_checkpoint") \
            .start()

    final_df_write_stream.awaitTermination()

def main():
    """
    Demo a use case of how can we use PySpark Structured Stream to consume the data from kafka as a stream
    and write back to kafka as a stream. The aggregration used her to to sum of product price grouped by orders

    """
    spark_it_up()

if __name__ == "__main__":
    main()
