from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from datetime import datetime


INTERNAL_ORDER = "internal_routed_order"
AGGR_TO_LOCATION = "aggregated_to_location"
KAFKA_BOOTSTRAP_SERVERS = '10.0.0.6:9092'
LOCATION_LOGISTICS = "location_logistics"


def get_pyspark_session():
    """
    Create spark session object.

    :input: None
    :output: Spark session object
    """
    session_object = SparkSession \
            .builder \
            .appName("PySpark Aggregate Order by to location") \
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
            .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
            .option("subscribe", INTERNAL_ORDER) \
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


    # Map the JSON object from the stream to the DF schema mentioned
    transformation_df2 = transformation_df1\
            .select(from_json(col("value"), df_detail_schema).alias("order_details"), "timestamp")

    # Convert the json object which is stored under value column onto multiple columns
    # based on the key name of the json object.
    transformation_df3 = transformation_df2.select("order_details.*", "timestamp")
    #transformation_df3.printSchema()

    # From the key of the message chose only order_id product id and to location
    # which is neede to compute the aggregated count of location 
    transformation_df4 = transformation_df3.select("product_id","to_location")

    # Aggregate product_price by gorder id
    transformation_df5 = transformation_df4.groupBy("to_location")\
            .agg({'product_id': 'count'}).select("to_location", \
            col("count(product_id)").alias("total_product"))

    # Write final datafram result into console 
    final_df_write_console = transformation_df4 \
            .writeStream \
            .trigger(processingTime='1 seconds') \
            .outputMode("update") \
            .option("truncate", "false")\
            .format("console") \
            .start()

    final_df_write_console = transformation_df5 \
            .writeStream \
            .trigger(processingTime='1 seconds') \
            .outputMode("update") \
            .option("truncate", "false")\
            .format("console") \
            .start()
    final_df_write_console.awaitTermination()

def main():
    """
    Demo a use case of how can we use PySpark Structured Stream to consume the data from kafka as a stream
    and write back to kafka as a stream. The aggregration used her to to count  of product 
    grouped by to_location

    """
    spark_it_up()


if __name__ == "__main__":
    main()
