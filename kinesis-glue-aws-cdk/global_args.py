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
    
    MONGODB_URL = ""  # MongoDB Atlas AWS CDK will create a MongoDB Cluster and will pass it to AWS Glue job stack.
    DATABASE_NAME = "etl-migration"
    COLLECTION_NAME = "etl-customer-demo"
    MONGODB_USER = ""
    MONGODB_PASSWORD = ""
    S3_BUCKET_NAME = "etl-bucket-demo"
    CUSTOMER_STREAM_NAME = "etl-kinesisStream-customer"
    ORDER_STREAM_NAME = "etl-kinesisStream-order"
    AUTH_DATABASE_NAME = "admin"
    ORG_ID = ""  # Your organization from MongoDB Atlas account
    REGION_NAME = "US_EAST_1"
    IP_ADDRESS = "0.0.0.0/0" # Use for development or testing purpose only
    IP_COMMENT = "AWS Glue CDK Test"
    PROFILE = "default"