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
    
    # MONGODB_URL: MongoDB Atlas AWS CDK will create a MongoDB Cluster and will pass newly created mongodb url to AWS Glue job stack.
    # MONGODB_USER/MONGODB_PASSWORD: For MongoDB username and password, we are directly setting it in mongodb stack and glue_job stack.
    
    DATABASE_NAME = "etl-migration"
    COLLECTION_NAME = "etl-customer-demo"
    S3_BUCKET_NAME = "etl-bucket-demo"
    CUSTOMER_STREAM_NAME = "etl-kinesisStream-customer"
    ORDER_STREAM_NAME = "etl-kinesisStream-order"
    AUTH_DATABASE_NAME = "admin"
    REGION_NAME = "US_EAST_1"
    IP_ADDRESS = "0.0.0.0/0" # Use for development or testing purposes only
    IP_COMMENT = "AWS Glue CDK Test"
    PROFILE = "default"

    INSTANCE_SIZE = "M0"
    EBS_VOLUME_TYPE = "STANDARD"
    BACKING_PROVIDER_NAME = "AWS"