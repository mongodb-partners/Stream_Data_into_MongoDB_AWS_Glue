class GlobalArgs():
    """
    Helper to define global statics
    """

    OWNER = "AWS_Glue_Data_Integration"
    ENVIRONMENT = "production"
    REPO_NAME = "kinesis-glue-etl"
    SOURCE_INFO = f"https://"
    VERSION = "2023_07_11"
    SUPPORT_EMAIL = ["", ]
    
    MONGODB_URL = ""
    DATABASE_NAME = "migration"
    COLLECTION_NAME = "customer_demo"
    MONGODB_USER = ""
    MONGODB_PASSWORD = ""
    S3_BUCKET_NAME = "etl-bucket-demo"
    CUSTOMER_STREAM_NAME = "kinesisStream-customer"
    ORDER_STREAM_NAME = "kinesisStream-order"
    AUTH_DATABASE_NAME = "admin"
    ORG_ID = ""
    REGION_NAME = "US_EAST_1"
    IP_ADDRESS = "0.0.0.0/0"
    IP_COMMENT = "AWS Glue CDK Test"
    PROFILE = "default"