from constructs import Construct
from aws_cdk import aws_iam as _iam
from aws_cdk import aws_s3_assets as _s3_assets
import aws_cdk as core
from aws_cdk import (
    Duration,
    Stack,
    aws_kinesis as kinesis,
    aws_glue as glue,
    aws_iam as iam,
    aws_sqs as sqs,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
)
from global_args import GlobalArgs

from dotenv import find_dotenv, load_dotenv
import os

class GlueJobStack(Stack):

    dotenv_path = find_dotenv();
    load_dotenv(dotenv_path);
    
    def __init__(
        self, 
        scope: Construct, 
        construct_id: str, 
        cust_src_stream,
        order_src_stream, 
        etl_bkt,
        mongodb_url,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        
        # Glue Job IAM Role
        self._glue_etl_role = _iam.Role(
            self, "glueJobRole",
            assumed_by=_iam.ServicePrincipal("glue.amazonaws.com"),
            managed_policies=[
                _iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonS3FullAccess"
                ),
                _iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSGlueServiceRole"
                )
            ]
        )
        self._glue_etl_role.add_to_policy(
            _iam.PolicyStatement(
                actions=[
                    "s3:*"
                ],
                resources=[
                    f"{etl_bkt.bucket_arn}",
                    f"{etl_bkt.bucket_arn}/*"
                ]
            )
        )

        self._glue_etl_role.add_to_policy(
            _iam.PolicyStatement(
                actions=[
                    "kinesis:DescribeStream"
                ],
                resources=[
                    f"{cust_src_stream.stream_arn}",
                    f"{order_src_stream.stream_arn}"
                ]
            )
        )

        cust_src_stream.grant_read(self._glue_etl_role)
        order_src_stream.grant_read(self._glue_etl_role)
        
        etl_script_asset = _s3_assets.Asset(
            self,
            "etlScriptAsset",
            path="glue_job_stack/glue_job_scripts/customer_kinesis_s3.py"
        )
        
        # Create a Glue Job for the customer

        username = os.getenv("MONGODB_USER")
        password = os.getenv("MONGODB_PASSWORD")   

        
        customer_job_name = 'CustomerGlueJob'
        customer_job = glue.CfnJob(
            self, 
            'CustomerGlueJob',
            name=customer_job_name,
            role=self._glue_etl_role.role_arn,
            command=glue.CfnJob.JobCommandProperty(
                name="gluestreaming",
                script_location="s3://{bucket}/{key}".format(
                    bucket=etl_script_asset.s3_bucket_name,
                    key=etl_script_asset.s3_object_key
                ),
                python_version="3"
            ),
            default_arguments={
                "--MONGODB_URL": mongodb_url+str("/test"),
                "--DATABASE_NAME": GlobalArgs.DATABASE_NAME,
                "--COLLECTION_NAME": GlobalArgs.COLLECTION_NAME,
                "--MONGODB_USER": username,
                "--MONGODB_PASSWORD": password,
                "--BUCKET_URL": str("s3://")+etl_bkt.bucket_name+str("/customer/"),
                "--STREAM_NAME":cust_src_stream.stream_name,
                "--enable-continuous-cloudwatch-log": "true", # Enable logging
                "--TempDir": str("s3://")+etl_bkt.bucket_name+str("/temporary/"),
                "--enable-spark-ui": "true",
                "--spark-event-logs-path":str("s3://")+etl_bkt.bucket_name+str("/sparkHistoryLogs/")

            },
            max_retries=0,
            glue_version="4.0",
            number_of_workers=2,
            worker_type="G.025X"
            )
        
        
        etl_script_asset = _s3_assets.Asset(
            self,
            "etlScriptAssetOrder",
            path="glue_job_stack/glue_job_scripts/order_kinesis_s3.py"
        )
        
        # Create Glue Job for order
        order_job_name = 'OrderGlueJob'
        order_job = glue.CfnJob(
            self, 'OrderGlueJob',
            name=order_job_name,
            role=self._glue_etl_role.role_arn,
            command=glue.CfnJob.JobCommandProperty(
                name="gluestreaming",
                script_location="s3://{bucket}/{key}".format(
                    bucket=etl_script_asset.s3_bucket_name,
                    key=etl_script_asset.s3_object_key
                ),
                python_version="3"
            ),
            default_arguments={
                "--MONGODB_URL": mongodb_url+str("/test"),
                "--DATABASE_NAME": GlobalArgs.DATABASE_NAME,
                "--COLLECTION_NAME": GlobalArgs.COLLECTION_NAME,
                "--MONGODB_USER": username,
                "--MONGODB_PASSWORD": password,
                "--BUCKET_URL": str("s3://")+etl_bkt.bucket_name+str("/order/"),
                "--STREAM_NAME":order_src_stream.stream_name,
                "--enable-continuous-cloudwatch-log": "true", # Enable logging
                "--TempDir": str("s3://")+etl_bkt.bucket_name+str("/temporary/"),
                "--enable-spark-ui": "true",
                "--spark-event-logs-path":str("s3://")+etl_bkt.bucket_name+str("/sparkHistoryLogs/")
            },
            max_retries=0,
            glue_version="4.0",
            number_of_workers=2,
            worker_type="G.025X"
            )

        # Output order job name
        core.CfnOutput(self, 'GlueJobName',
                       value=order_job.name)
