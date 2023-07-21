from constructs import Construct
import aws_cdk as core
from aws_cdk import (
    Duration,
    RemovalPolicy,
    aws_iam as iam,
    aws_ec2 as ec2,
    aws_s3 as _s3,
    aws_kinesis as kinesis,
    aws_s3_deployment as s3deploy,
    aws_mwaa as mwaa,
    aws_kms as kms,
    Stack,
    CfnOutput,
    Tags,
    App
)

class KinesisGlueAwsCdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, cust_stream_name: str, 
                 order_stream_name: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create Kinesis Data Stream for Customer
        self.customer_stream_name = cust_stream_name
        shard_count = 1  # Set the desired number of shards for the stream
        self.cust_stream = kinesis.Stream(
            self, 
            'KinesisStreamCustomer',
            retention_period=Duration.days(1),
            stream_name=self.customer_stream_name,
            shard_count=shard_count
        )
        
         # Create Kinesis Data Stream for Order   
        self.order_stream_name = order_stream_name
        shard_count = 1  # Set the desired number of shards for the stream
        self.order_stream = kinesis.Stream(
            self, 
            'KinesisStreamOrder',
            retention_period=Duration.days(1),
            stream_name=self.order_stream_name,
            shard_count=shard_count
        )

        # Output the stream ARN and job name
        output_0 = core.CfnOutput(
            self, 
            'CustomerOrderKinesisDataStream',
            value=self.cust_stream.stream_arn,
            description="Ingesting customer and order data to Kinesis stream.",
        )

    
    # properties to share with other stacks
    @property
    def get_customer_stream(self):
        return self.cust_stream
    @property
    def get_order_stream(self):
        return self.order_stream