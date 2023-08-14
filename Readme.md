# Stream data into MongoDB Atlas using AWS Glue

## Introduction: 
It demonstrates the seamless integration of AWS Glue, AWS Kinesis, and MongoDB Atlas has emerged as a powerful solution for ETL (Extract, Transform, Load) operations, offering seamless data flow and efficient management across diverse environments.

It demonstrates a CDK app with an instance of a stack (`kinesis-glue-aws-cdk`)

## [MongoDB Atlas](https://www.mongodb.com/atlas) 
MongoDB Atlas is an all-purpose database having features like Document Model, Geo-spatial, Time Series, Hybrid deployment, and multi-cloud services.
It evolved as a "Developer Data Platform", intended to reduce the developers' workload  and management of the database environment.
It also provides a free tier to test out the application/database features.

## [AWS Glue](https://aws.amazon.com/glue/)

AWS Glue is a fully managed serverless data integration service that makes it easy to extract, transform, and load (ETL) from various data sources for analytics and data processing with Apache Spark ETL jobs. In this application, we will receive incoming requests from producers and process them using Glue Jobs to store them in S3 and MongoDB. Let us assume each request produces an event like the one shown below,

## [Amazon Kinesis](https://aws.amazon.com/kinesis/)

Amazon Kinesis cost-effectively processes and analyzes streaming data at any scale as a fully managed service. With Kinesis, you can ingest real-time data, such as video, audio, application logs, website clickstreams, and IoT telemetry data, for machine learning (ML), analytics, and other applications.
#
## Architecture Diagram:

<img width="962" alt="image" src="https://github.com/mongodb-partners/Stream_Data_into_MongoDB_AWS_Glue/assets/101570105/2551fcb1-bf63-4b8b-8b44-f3485901c9e3">

## Implementation Steps

1.  ## Prerequisites

    This demo, instructions, scripts, and cloudformation template are designed to be run in `us-east-1`. With a few modifications, you can try it out in other regions as well.

    -  AWS CLI Installed & Configured 
    -  AWS CDK Installed & Configured
    -  MongoDB Atlas Account 
    -  Python Packages :
      - Python3 - `yum install -y python3`
      - Python Pip - `yum install -y python-pip`
      - Virtualenv - `pip3 install virtualenv`

1.  ## Setting up the environment

    - Get the application code

      ```bash
      git clone https://github.com/mongodb-partners/Stream_Data_into_MongoDB_AWS_Glue
      cd kinesis-glue-aws-cdk
      ```

1.  ## Prepare the dev environment to run AWS CDK

    a. Setup the AWS Environment AWS Access Key ID, AWS Secret Access Key, and optionally AWS Session Token
    

    b. We will use `cdk` to make our deployments easier. Let's go ahead and install the necessary components.

    ```bash
    # You should have npm pre-installed
    # If you DONT have cdk installed
    npm install -g aws-cdk

    # Make sure you in root directory
    python3 -m venv .venv
    source .venv/bin/activate
    pip3 install -r requirements.txt
    ```
    Side Note: for development setup use requirements-dev.txt

    c. Set up the CDK bootstrapping

        
        cdk bootstrap

       d. update the relevant parameters in global_args.py
       
       * Update the `OrgId` Organization ID from your MongoDB Atlas account. 
       * Please note that, Using "0.0.0.0/0" as an `IP_ADDRESS` we are allowing access from anywhere. This might be suitable for development or testing purposes but is highly discouraged for production environments because it exposes the database to potential attacks from unauthorized sources.

       <br>

       e. list the cdks

        cdk ls

     Follow on-screen prompts

   You should see an output of the available stacks,
    
        aws-etl-mongo-atlas-stack
        aws-etl-kinesis-stream-stack
        aws-etl-bucket-stack
        aws-etl-glue-job-stack


1.  ##  Deploying the application

    Let us walk through each of the stacks,

    ### **Stack: aws-etl-mongo-atlas-stack**

      This stack will create MongoDB Atlas Free tier Cluster.

      **Prerequisite:**
      
      a. create a role with its trust relationship as a CloudFormation service

      Use [this template](https://github.com/mongodb/mongodbatlas-cloudformation-resources/blob/master/examples/execution-role.yaml) to create a [new CloudFormation stack](https://console.aws.amazon.com/cloudformation/home#/stacks/create) to create the execution role.

      Execution Role stack:

      ![AWS Glue Data Integration: Streaming ETL with AWS Glue](kinesis-glue-aws-cdk/images/execution_role_stack_output.png)

      b.The following Public Extension in the Cloudormation Registry should be activated with the Role created earlier step. Use [this link](https://us-east-1.console.aws.amazon.com/cloudformation/home?region=us-east-1#/registry/public-extensions?visibility=PUBLIC&type=RESOURCE&category=THIRD_PARTY) to register extensions on CloudFormation.
      
              MongoDB::Atlas::Project,
              MongoDB::Atlas::DatabaseUser,
              MongoDB::Atlas::Cluster,
              MongoDB::Atlas::ProjectIpAccessList

      Pass the ARN of the role from the earlier step as an input to activate the MongoDB resource in Public Extension.

      MongoDB Resource Activation in Public Extension:

      ![AWS Glue Data Integration: Streaming ETL with AWS Glue](kinesis-glue-aws-cdk/images/activate_mongodb_resource.png)
    
      c. Login to MongoDB console and note down the organization ID in which you want to create the database cluster
      
      d. create an API Key in an organization for the organization with Project Owner access and not down API credentials
      
      e. Store the Organization API in AWS Secret Manager
   
      A profile should be created in the AWS Secrets Manager, containing the MongoDB Atlas Programmatic API Key.

      Use [this template](https://github.com/mongodb/mongodbatlas-cloudformation-resources/blob/master/examples/profile-secret.yaml) to create a [new CloudFormation stack](https://console.aws.amazon.com/cloudformation/home#/stacks/create) for the default profile that all resources will attempt to use unless a different override is specified.

      **Profile secret Stack:**

      ![AWS Glue Data Integration: Streaming ETL with AWS Glue](kinesis-glue-aws-cdk/images/profile_secret_mongodb_API.png)

    

      Initiate the deployment with the following command,

      ```bash
      cdk deploy aws-etl-mongo-atlas-stack
      ```

      After successfully deploying the stack, Check the `Outputs` section of the stack. You will find the `stdUrl` and `stdSrvUrl` for connection string.

      **Stack:**

      ![AWS Glue Data Integration: Streaming ETL with AWS Glue](kinesis-glue-aws-cdk/images/mongo_atlas_stack_output.png)

      **MongoDB Atlas Cluster:**

      ![AWS Glue Data Integration: Streaming ETL with AWS Glue](kinesis-glue-aws-cdk/images/mongodb_atlas_cluster.png)

    - ###  **Stack: aws-etl-kinesis-stream-stack**

      This stack will create two kinesis data streams. Each producer runs for an ingesting stream of events for different customers with their orders. 

      Initiate the deployment with the following command,

      ```bash
      cdk deploy aws-etl-kinesis-stream-stack
      ```

      After successfully deploying the stack, Check the `Outputs` section of the stack. You will find the `CustomerOrderKinesisDataStream` kinesis function.

      Stack:

      ![AWS Glue Data Integration: Streaming ETL with AWS Glue](kinesis-glue-aws-cdk/images/aws_kinesis_stream_stack_output.png)

      Amazon Kinesis Data Stream:

      ![AWS Glue Data Integration: Streaming ETL with AWS Glue](kinesis-glue-aws-cdk/images/aws_kinesis_stream.png)


    - ### **Stack: aws-etl-bucket-stack**

      This stack will create an S3 bucket that will be used by AWS Glue jobs to persist the incoming customer and order details.

      ```bash
      cdk deploy aws-etl-bucket-stack
      ```

      After successfully deploying the stack, Check the `Outputs` section of the stack. You will find the `S3SourceBucket` resource.

      **Stack:**

      ![AWS Glue Data Integration: Streaming ETL with AWS Glue](kinesis-glue-aws-cdk/images/aws_s3_bucket_stack_output.png)

      AWS S3 Bucket:

      ![AWS Glue Data Integration: Streaming ETL with AWS Glue](kinesis-glue-aws-cdk/images/aws_s3_bucket.png)

    - ### **Stack: aws-etl-glue-job-stack**

      This stack will create two AWS Glue Jobs. One job for the customer and another for order. The code is in this location `glue_job_stack/glue_job_scripts/customer_kinesis_streams_s3.py` and `glue_job_stack/glue_job_scripts/order_kinesis_streams_s3.py`

      ```bash
      cdk deploy aws-etl-glue-job-stack
      ```

     ** Stack:**

      ![AWS Glue Data Integration: Streaming ETL with AWS Glue](kinesis-glue-aws-cdk/images/aws_glue_job_stack_output.png)

      **AWS Glue Job:**

      ![AWS Glue Data Integration: Streaming ETL with AWS Glue](kinesis-glue-aws-cdk/images/aws_glue_job.png)

      ** Note **

      Please note that, this CDK application creates MongoDB Atlas Free tier Cluster, as shown in above screen(No.1 & 2). You don't have to create it manuallay. Also, the url of the newly created cluster will be passed to AWS Glue job as a mongodb url paramter.

      Location details for "Spark UI logs path" and "Temporary path" will be determined automatically based on current logged-in account.

      **Spark UI logs path:**
      
      `s3://aws-glue-assets-<ACCOUNT_ID>-<REGION_NAME>/sparkHistoryLogs` 

     ** Temporary path:**

      `s3://aws-glue-assets-<ACCOUNT_ID>-<REGION_NAME>/temporary/`

    Though, You can always pass the parameters using the steps mentioned below.

    - ** Update AWS Glue Studio parameters**
    
    <br>
    In Job Details tab, update the AWS Glue stuido advanced paramters for MongoDB Atlas URI, User Name and Password. 

<img width="876" alt="image" src="https://github.com/mongodb-partners/Stream_Data_into_MongoDB_AWS_Glue/assets/101570105/00d918df-fd28-4506-909a-3f16723a6024">

    
Once you are ready with all stacks, start the producers for the customer and order The code is in this location

      `producer/customer.py` and `producer/order.py`
      
to ingest data into a kinesis data stream and also start the Glue job for both.


#

` Sample record in MongoDB Atlas:`

```json
{
  "_id": "1",
  "country_id": "1",
  "customer_name": "NICK",
  "email_id": "nick@gmail.com",
  "orders": [
    {
      "order_id": "8",
      "product_name": "Artisanal Cheese Selection",
      "quantity": "8",
      "price": "29.17"
    }
  ]
}
```
#

## **Clean up**

Use `cdk destroy` to clean up all the AWS CDK resources. 
Terminate the MongoDB Atlas cluster.

## Troubleshooting

Refer [this link](https://github.com/mongodb/mongodbatlas-cloudformation-resources/tree/master#troubleshooting) to resolve some common issues encountered when using AWS CloudFormation/CDK with MongoDB Atlas Resources.

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!
