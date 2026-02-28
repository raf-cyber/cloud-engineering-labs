import boto3

REGION_NAME = 'us-east-1'

s3_client = boto3.client('s3', REGION_NAME)
org = boto3.client("organizations")

org.describe_organization()