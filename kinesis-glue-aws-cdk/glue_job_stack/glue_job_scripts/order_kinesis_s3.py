import sys
import logging
import boto3
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import struct
from pyspark.sql.functions import collect_list, expr

from pyspark.sql import DataFrame, Row
import datetime
from awsglue import DynamicFrame

logger = logging.getLogger()
logger.setLevel(logging.INFO)

args = getResolvedOptions(sys.argv, ["JOB_NAME","MONGODB_URL","DATABASE_NAME","COLLECTION_NAME",
"MONGODB_USER","MONGODB_PASSWORD","BUCKET_URL", "STREAM_NAME"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

def get_aws_region():
    # Create a new session using the default credentials and configuration
    session = boto3.Session()
    return session.region_name

def get_aws_account_id():
    # Create a new session using the default credentials and configuration
    session = boto3.Session()
    return session.client('sts').get_caller_identity().get('Account')

aws_region = get_aws_region()
aws_account_id = get_aws_account_id()

# Construct the stream ARN
stream_arn = f"arn:aws:kinesis:{aws_region}:{aws_account_id}:stream/"+args['STREAM_NAME']

dataframe_KinesisStream_node1 = glueContext.create_data_frame.from_options(
    connection_type="kinesis",
    connection_options={
        "typeOfData": "kinesis",
        "streamARN": stream_arn,
        "classification": "json",
        "startingPosition": "earliest",
        "inferSchema": "true",
    },
    transformation_ctx="dataframe_KinesisStream_node1",
)

write_mongo_options = {
    "connection.uri": args['MONGODB_URL'],
    "database": args['DATABASE_NAME'],
    "collection": args['COLLECTION_NAME'],
    "username": args['MONGODB_USER'],
    "password": args['MONGODB_PASSWORD'],
    "replaceDocument": "false",
    "partitioner": "MongoSamplePartitioner",
    "partitionerOptions.partitionSizeMB": "10",
    "partitionerOptions.partitionKey": "_id"
}

order_ds = glueContext.create_dynamic_frame_from_options(connection_type = "s3", connection_options={"paths": [args['BUCKET_URL']]}, format="json", format_options={}, transformation_ctx = "")

order_df = order_ds.toDF()

def processBatch(data_frame, batchId):
    global order_df
    
    if data_frame.count() > 0:
        
        KinesisStream_node1 = DynamicFrame.fromDF(
            data_frame, glueContext, "from_data_frame"
        )

        ApplyMapping_node2 = ApplyMapping.apply(
            frame=KinesisStream_node1,
            mappings=[],
            transformation_ctx="ApplyMapping_node2",
        )

        now = datetime.datetime.now()
        year = now.year
        month = now.month
        day = now.day
        hour = now.hour

        logger = glueContext.get_logger()

        S3bucket_node3_path = (args['BUCKET_URL'])
        
        S3bucket_node3 = glueContext.write_dynamic_frame.from_options(
            frame=KinesisStream_node1,
            connection_type="s3",
            format="json",
            connection_options={"path": S3bucket_node3_path, "partitionKeys": []},
            transformation_ctx="S3bucket_node3",
        )
        
        logger.info("New order has been inserted into s3 bucket.")
    
        order_df.show(n=5)
        logger.info("Merging new and old orders...")

        changed_orders = KinesisStream_node1.toDF()
        
        logger.info("Checking if there are any existing orders present in bucket.")
        
        if "customer_id" in order_df.columns:
         order_df = order_df.union(changed_orders)
        else:
         order_df = changed_orders
        
        logger.info("Selecting only changed orders.")
        limited_orders = changed_orders.select("customer_id").withColumnRenamed("customer_id", "cust_id")
        
        limited_orders = order_df.join(limited_orders, order_df.customer_id == limited_orders.cust_id, "inner")
        
        order_struct = struct("order_id", "product_name", "quantity", "price")

        nested_orders = limited_orders.groupBy("customer_id").agg(struct(collect_list(order_struct)).alias("orders")).withColumnRenamed("customer_id", "_id")
        nested_orders = nested_orders.withColumn("orders", expr("orders.col1"))
        
        order_dynamic_frame = DynamicFrame.fromDF(nested_orders, glueContext, "order_dynamic_frame")
        
        logger.info("Writing to MongoDB...")

        glueContext.write_dynamic_frame.from_options(order_dynamic_frame, connection_type="mongodb", connection_options=write_mongo_options)
        logger.info("MongoDB Write Done...")


glueContext.forEachBatch(
    frame=dataframe_KinesisStream_node1,
    batch_function=processBatch,
    options={
        "windowSize": "100 seconds",
        "checkpointLocation": args["TempDir"] + "/" + args["JOB_NAME"] + "/checkpoint/",
    },
)
job.commit()
