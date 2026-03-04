import boto3
import json

try:
    with open('data.json', 'r') as file:
        data = json.load(file)
except FileNotFoundError:
    print("Error: The file data.json was not found")
except json.JSONDecodeError:
    print("Failed to decode JSON file. Incorrect JSON format")


def check_for_wildcard_key(bucket_name, potential_key_with_wildcard):
    s3 = boto3.client('s3')
    try:
        s3.head_object(Bucket=bucket_name, Key=potential_key_with_wildcard)
        print(f"Object with key '{potential_key_with_wildcard}' exists.")
        return True
    except s3.exceptions.ClientError as e:
        if e.response['Error']['Code'] in ['404', 'NoSuchKey', '403']:
            print(f"Object with key '{potential_key_with_wildcard}' does not exist, or you lack permissions.")
            return False
        else:
            raise e


def check_for_iam_user(iam_user_name):
    iam = boto3.client('iam')
    try:
        response = iam.get_user(UserName=iam_user_name)
        print(f"IAM user '{iam_user_name}' exists.")
        return True
    except iam.exceptions.NoSuchEntityException:
        print(f"IAM user '{iam_user_name}' does not exist.")
        return False
    except iam.exceptions.ClientError as e:
        raise e