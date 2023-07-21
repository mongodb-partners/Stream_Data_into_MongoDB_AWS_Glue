#!/usr/bin/env python3

import aws_cdk as cdk
from glue_job_stack.glue_job_stack import GlueJobStack
from kinesis_glue_aws_cdk.kinesis_glue_aws_cdk_stack import KinesisGlueAwsCdkStack
from s3_stack.s3_stack import S3Stack
from global_args import GlobalArgs

app = cdk.App()

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
    etl_bkt = etl_bkt_stack.data_bkt
)

app.synth()