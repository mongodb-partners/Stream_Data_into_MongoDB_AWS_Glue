# Stream data into MongoDB Atlas using AWS Glue

## Introduction: 
In this GitHub repository, you'll find a tangible showcase of how AWS Glue, Amazon Kinesis, and MongoDB Atlas seamlessly integrate, creating a streamlined data streaming solution alongside Extract, Transform, and Load (ETL) capabilities. This repository also harnesses the power of AWS CDK to automate deployment across diverse environments, enhancing the efficiency of the entire process.


## MongoDB Atlas 
[MongoDB Atlas](https://www.mongodb.com/atlas) is an all-purpose database having features like Document Model, Geo-spatial, Time Series, Hybrid deployment, and multi-cloud services. It evolved as a "Developer Data Platform", intended to reduce the developers' workload  and management of the database environment. It also provides a free tier to test out the application/database features.

## AWS Glue

[AWS Glue](https://aws.amazon.com/glue/) is a fully managed serverless data integration service that makes it easy to extract, transform, and load (ETL) from various data sources for analytics and data processing with Apache Spark ETL jobs. In this application, we will receive incoming requests from producers and process them using Glue Jobs to store them in S3 and MongoDB. 

## Amazon Kinesis

[Amazon Kinesis](https://aws.amazon.com/kinesis/) cost-effectively processes and analyzes streaming data at any scale as a fully managed service. With Kinesis, you can ingest real-time data, such as video, audio, application logs, website clickstreams, and IoT telemetry data, for machine learning (ML), analytics, and other applications.


## Architecture Diagram:

<img width="971" alt="image" src="https://github.com/mongodb-partners/Stream_Data_into_MongoDB_AWS_Glue/assets/101570105/556dbe2f-e13f-4ff8-98e9-4991e6381d85">



## Implementation Steps

1.  ## Prerequisites

    This demo, instructions, scripts, and cloudformation template are designed to be run in `us-east-1`. With a few modifications, you can try it out in other regions as well.

    -  [AWS CLI Installed & Configured](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
    -  [NVM / NPM installed & Configured](https://nvm.sh) 
    -  [AWS CDK Installed & Configured](https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html) 
    -  [MongoDB Atlas Account](https://www.mongodb.com/docs/atlas/tutorial/create-atlas-account/) and set up the [Organization](https://www.mongodb.com/docs/atlas/government/tutorial/create-organization/#create-an-organization) 
    -  [Python Packages](https://www.python.org/downloads/):
          - [Python3](https://packaging.python.org/en/latest/tutorials/installing-packages/#ensure-you-can-run-python-from-the-command-line) - `yum install -y python3`
          - [Python Pip](https://packaging.python.org/en/latest/tutorials/installing-packages/#ensure-you-can-run-pip-from-the-command-line) - `yum install -y python-pip`
          - [Virtualenv](https://docs.python.org/3/library/venv.html) - `pip3 install virtualenv`

1.  ## Setting up the environment

    - Get the application code

      ```bash
      git clone https://github.com/mongodb-partners/Stream_Data_into_MongoDB_AWS_Glue
      cd kinesis-glue-aws-cdk
      ```

1.  ## Prepare the dev environment to run AWS CDK

    a. Setup the [AWS Environment variable](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-envvars.html) AWS Access Key ID, AWS Secret Access Key, and optionally AWS Session Token

           export AWS_ACCESS_KEY_ID = <"your AWS access key">
           export AWS_SECRET_ACCESS_KEY =<"your AWS secret access key">
           export AWS_SESSION_TOKEN = <"your AWS session token">
    

    b. We will use `cdk` to make our deployments easier. .

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

    c. [Bootstrap](https://docs.aws.amazon.com/cdk/v2/guide/bootstrapping.html) the application with AWS Account

        
        cdk bootstrap
    

       d. update the OrgID parameters in global_args.py
       
       * Update the `OrgId` Organization ID from your MongoDB Atlas account.
  
         <img width="1159" alt="image" src="https://github.com/mongodb-partners/Stream_Data_into_MongoDB_AWS_Glue/assets/101570105/f1f5c45d-557b-4c5b-8035-b4472723ddfc">
         

       * Please note that using "0.0.0.0/0" as an `IP_ADDRESS` we are allowing access to the database from anywhere. This might be suitable for development or testing purposes but is **highly discouraged** for production environments because it exposes the database to potential attacks from unauthorized sources. 

       <br>

       e. list the cdks

        cdk ls

   You should see an output of the available stacks,
    
        aws-etl-mongo-atlas-stack
        aws-etl-kinesis-stream-stack
        aws-etl-bucket-stack
        aws-etl-glue-job-stack


##  Deploying the application

Let us walk through each of the stacks,

### **Stack for MongoDB Atlas: aws-etl-mongo-atlas-stack**

This stack will create MongoDB Atlas Project and a free tier database cluster with a user and network permission (Open).

**Prerequisite:**
      
a. create an AWS role with its trust relationship as a CloudFormation service

Use [this template](https://github.com/mongodb/mongodbatlas-cloudformation-resources/blob/master/examples/execution-role.yaml) to create a [new CloudFormation stack](https://console.aws.amazon.com/cloudformation/home#/stacks/create) to create the execution role.


![AWS Glue Data Integration: Streaming ETL with AWS Glue](kinesis-glue-aws-cdk/images/execution_role_stack_output.png)

b.The following Public Extension in the Cloudormation Registry should be activated with the Role created earlier step. Use [this link](https://us-east-1.console.aws.amazon.com/cloudformation/home?region=us-east-1#/registry/public-extensions?visibility=PUBLIC&type=RESOURCE&category=THIRD_PARTY) to register extensions on CloudFormation.
      
              MongoDB::Atlas::Project,
              MongoDB::Atlas::DatabaseUser,
              MongoDB::Atlas::Cluster,
              MongoDB::Atlas::ProjectIpAccessList

Pass the ARN of the role from the earlier step as input to activate the MongoDB resource in Public Extension.

MongoDB Resource Activation in Public Extension:

![AWS Glue Data Integration: Streaming ETL with AWS Glue](kinesis-glue-aws-cdk/images/activate_mongodb_resource.png)

Alternatively, you can activate the above public extension through AWS CLI also.

Command to list the MongoDB Public Extensions. Note the down the arns for the above four public extension.

    aws cloudformation list-types \
      --visibility PUBLIC \
      --filters "Category=THIRD_PARTY,TypeNamePrefix=Mongodb"

Command to activate the Public Extension. Use this command to activate all the four public extension mentioned in the previous steps.

    aws cloudformation activate-type --region us-east-1 --public-type-arn "<arn for the public extension noted down in the previous step>" --execution-role-arn "<arn of the role created in step a>"

    
c. Login to MongoDB console and note down the organization ID. Ensure the Organization ID is updated in the global_args.py

<img width="1159" alt="image" src="https://github.com/mongodb-partners/Stream_Data_into_MongoDB_AWS_Glue/assets/101570105/f1f5c45d-557b-4c5b-8035-b4472723ddfc">
      
d. create an [API Key](https://www.mongodb.com/docs/atlas/configure-api-access/#create-an-api-key-in-an-organization) in an organization with Organization Owner and Organization Project Creation access. Note down API credentials

<img width="762" alt="image" src="https://github.com/mongodb-partners/Stream_Data_into_MongoDB_AWS_Glue/assets/101570105/93f2a8f7-909d-44ed-a8ea-da037c42b8a6">

      
e. A profile should be created in the AWS Secrets Manager, containing the MongoDB Atlas Programmatic API Key.

Use [this template](https://github.com/mongodb/mongodbatlas-cloudformation-resources/blob/master/examples/profile-secret.yaml) to create a [new CloudFormation stack](https://console.aws.amazon.com/cloudformation/home#/stacks/create) for the default profile that all resources will attempt to use unless a different override is specified.

**Profile secret Stack:**

![AWS Glue Data Integration: Streaming ETL with AWS Glue](kinesis-glue-aws-cdk/images/profile_secret_mongodb_API.png)

    

Initiate the deployment with the following command,

      ```bash
      cdk deploy aws-etl-mongo-atlas-stack
      ```

After successfully deploying the stack, validate the `Outputs` section of the stack and MongoDB Atlas cluster. You will find the `stdUrl` and `stdSrvUrl` for connection string.

**Stack:**

![AWS Glue Data Integration: Streaming ETL with AWS Glue](kinesis-glue-aws-cdk/images/mongo_atlas_stack_output.png)

**MongoDB Atlas Cluster:**

![AWS Glue Data Integration: Streaming ETL with AWS Glue](kinesis-glue-aws-cdk/images/mongodb_atlas_cluster.png)


- ###  **Stack for creating the Kinesis Stream: aws-etl-kinesis-stream-stack**

This stack will create two kinesis data streams. Each producer runs for an ingesting stream of events for different customers with their orders. 

Initiate the deployment with the following command,

      ```bash
      cdk deploy aws-etl-kinesis-stream-stack
      ```

After successfully deploying the stack, Check the `Outputs` section of the stack. You will find the `CustomerOrderKinesisDataStream` kinesis function.

**Stack:**

![AWS Glue Data Integration: Streaming ETL with AWS Glue](kinesis-glue-aws-cdk/images/aws_kinesis_stream_stack_output.png)

**Amazon Kinesis Data Stream:**

![AWS Glue Data Integration: Streaming ETL with AWS Glue](kinesis-glue-aws-cdk/images/aws_kinesis_stream.png)


- ### **Stack for creating the S3 bucket: aws-etl-bucket-stack**

This stack will create an S3 bucket that will be used by AWS Glue jobs to persist the incoming customer and order details.

      ```bash
      cdk deploy aws-etl-bucket-stack
      ```

After successfully deploying the stack, Check the `Outputs` section of the stack. You will find the `S3SourceBucket` resource.

**Stack:**

![AWS Glue Data Integration: Streaming ETL with AWS Glue](kinesis-glue-aws-cdk/images/aws_s3_bucket_stack_output.png)

**AWS S3 Bucket:**

![AWS Glue Data Integration: Streaming ETL with AWS Glue](kinesis-glue-aws-cdk/images/aws_s3_bucket.png)


- ### **Stack for creating the AWS Glue job and paramters: aws-etl-glue-job-stack**

This stack will create two AWS Glue Jobs. One job for the customer and another for order. The code is in this location `glue_job_stack/glue_job_scripts/customer_kinesis_streams_s3.py` and `glue_job_stack/glue_job_scripts/order_kinesis_streams_s3.py`

      ```bash
      cdk deploy aws-etl-glue-job-stack
      ```

** Stack:**

![AWS Glue Data Integration: Streaming ETL with AWS Glue](kinesis-glue-aws-cdk/images/aws_glue_job_stack_output.png)

**AWS Glue Job:**

![AWS Glue Data Integration: Streaming ETL with AWS Glue](kinesis-glue-aws-cdk/images/aws_glue_job.png)

** Note **

This CDK application creates MongoDB Atlas Free tier Cluster, as shown in above screen(No.1 & 2). You don't have to create it manuallay. Also, the url of the newly created cluster will be passed to AWS Glue job as a mongodb url paramter.

Location details for "Spark UI logs path" and "Temporary path" will be determined automatically based on current logged-in account.

**Spark UI logs path:**
      
      `s3://aws-glue-assets-<ACCOUNT_ID>-<REGION_NAME>/sparkHistoryLogs` 

** Temporary path:**

      `s3://aws-glue-assets-<ACCOUNT_ID>-<REGION_NAME>/temporary/`

Though, You can always pass the parameters using the steps mentioned below.

- ** Update AWS Glue Studio parameters**
    
    <br>

    
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
