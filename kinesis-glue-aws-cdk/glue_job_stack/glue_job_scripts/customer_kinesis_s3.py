import sys
import logging
import boto3
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import collect_list, expr

from pyspark.sql import DataFrame, Row
import datetime
from awsglue import DynamicFrame

args = getResolvedOptions(sys.argv, ["JOB_NAME","MONGODB_URL","DATABASE_NAME","COLLECTION_NAME",
"MONGODB_USER","MONGODB_PASSWORD","BUCKET_URL", "STREAM_NAME"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

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

def processBatch(data_frame, batchId):

    if data_frame.count() > 0:
        
        KinesisStream_node1 = DynamicFrame.fromDF(
            data_frame,
            glueContext,
            "from_data_frame",
        )
        
        ApplyMapping_node2 = ApplyMapping.apply(
            frame=KinesisStream_node1,
            mappings=[
                ("customer_id", "int", "_id", "int"),
                ("customer_name", "string", "customer_name", "string"),
                ("email_id", "string", "email_id", "string"),
                ("country_id", "int", "country_id", "int"),
            ],
            transformation_ctx="ApplyMapping_node2",
        )
        
        S3bucket_node3_path = (args['BUCKET_URL'])
        
        customer_df = KinesisStream_node1.toDF()
        logger.info("====================")
        customer_df.show(n=5)
        logger.info("====================")
        
        customer_df = customer_df.withColumn("_id", expr("customer_id")).drop("customer_id")
        
        customer_dynamic_frame = DynamicFrame.fromDF(customer_df, glueContext, "customer_dynamic_frame")
        
        S3bucket_node3 = glueContext.write_dynamic_frame.from_options(
            frame=customer_dynamic_frame,
            connection_type="s3",
            format="json",
            connection_options={"path": S3bucket_node3_path, "partitionKeys": []},
            transformation_ctx="S3bucket_node3",
        )

        glueContext.write_dynamic_frame.from_options(
            customer_dynamic_frame, 
            connection_type="mongodb", 
            connection_options=write_mongo_options
        )


glueContext.forEachBatch(
    frame=dataframe_KinesisStream_node1,
    batch_function=processBatch,
    options={
        "windowSize": "100 seconds",
        "checkpointLocation": args["TempDir"] + "/" + args["JOB_NAME"] + "/checkpoint/",
    },
)
job.commit()
