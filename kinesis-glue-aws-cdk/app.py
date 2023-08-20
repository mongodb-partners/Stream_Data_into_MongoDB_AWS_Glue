#!/usr/bin/env python3

import aws_cdk as cdk
from glue_job_stack.glue_job_stack import GlueJobStack
from kinesis_glue_aws_cdk.kinesis_glue_aws_cdk_stack import KinesisGlueAwsCdkStack
from s3_stack.s3_stack import S3Stack
from global_args import GlobalArgs
from mongodb_atlas_stack.mongodb_atlas_stack import MongoDBAtlasStack

app = cdk.App()

# MongoDB AtlasBasic stack
etl_mongo_atlas_stack = MongoDBAtlasStack(
    app, 
    f"{app.node.try_get_context('project')}-mongo-atlas-stack"
)

# Kinesis data stream
etl_kinesis_stack = KinesisGlueAwsCdkStack(
    app,
    f"{app.node.try_get_context('project')}-kinesis-stream-stack",
    cust_stream_name = GlobalArgs.CUSTOMER_STREAM_NAME,
    order_stream_name = GlobalArgs.ORDER_STREAM_NAME,
)

# S3 Bucket to hold our datasources
etl_bkt_stack = S3Stack(
    app,
    f"{app.node.try_get_context('project')}-bucket-stack",
    stack_log_level = "INFO",
    custom_bkt_name = GlobalArgs.S3_BUCKET_NAME,
    description = "Data Integration Demo: S3 Bucket to hold our datasources"
)

# Glue Job Stack
etl_glue_job_stack = GlueJobStack(
    app,
    f"{app.node.try_get_context('project')}-glue-job-stack",
    cust_src_stream = etl_kinesis_stack.get_customer_stream,
    order_src_stream = etl_kinesis_stack.get_order_stream,
    etl_bkt = etl_bkt_stack.data_bkt,
    mongodb_url = etl_mongo_atlas_stack.get_connection_string_srv
)

# Get all the stacks
cdk.Tags.of(etl_bkt_stack).add("owner", GlobalArgs.TAG_OWNER)
cdk.Tags.of(etl_bkt_stack).add("purpose", GlobalArgs.TAG_PURPOSE)
cdk.Tags.of(etl_bkt_stack).add("expire-on", GlobalArgs.TAG_EXPIRE_ON)
cdk.Tags.of(etl_bkt_stack).add("cdk_stack", "aws-etl-bkt-stack")

cdk.Tags.of(etl_glue_job_stack).add("owner", GlobalArgs.TAG_OWNER)
cdk.Tags.of(etl_glue_job_stack).add("purpose", GlobalArgs.TAG_PURPOSE)
cdk.Tags.of(etl_glue_job_stack).add("expire-on", GlobalArgs.TAG_EXPIRE_ON)
cdk.Tags.of(etl_glue_job_stack).add("cdk_stack", "aws-etl-glue-job-stack")

cdk.Tags.of(etl_kinesis_stack).add("owner", GlobalArgs.TAG_OWNER)
cdk.Tags.of(etl_kinesis_stack).add("purpose", GlobalArgs.TAG_PURPOSE)
cdk.Tags.of(etl_kinesis_stack).add("expire-on", GlobalArgs.TAG_EXPIRE_ON)
cdk.Tags.of(etl_kinesis_stack).add("cdk_stack", "aws-etl-kinesis-stack")

cdk.Tags.of(etl_mongo_atlas_stack).add("owner", GlobalArgs.TAG_OWNER)
cdk.Tags.of(etl_mongo_atlas_stack).add("purpose", GlobalArgs.TAG_PURPOSE)
cdk.Tags.of(etl_mongo_atlas_stack).add("expire-on", GlobalArgs.TAG_EXPIRE_ON)
cdk.Tags.of(etl_mongo_atlas_stack).add("cdk_stack", "aws-etl-mongo-atlas-stack")


app.synth()
