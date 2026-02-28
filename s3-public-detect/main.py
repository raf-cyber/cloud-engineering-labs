import boto3
from botocore.exceptions import ClientError

s3 = boto3.client("s3")

def check_public_access_block(bucket):
    try:
        response = s3.get_public_access_block(Bucket=bucket)
        config = response["PublicAccessBlockConfiguration"]
        return not all(config.values())
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchPublicAccessBlockConfiguration":
            return True
        raise

def check_bucket_acl(bucket):
    response = s3.get_bucket_acl(Bucket=bucket)
    for grant in response["Grants"]:
        grantee = grant["Grantee"]
        if grantee["Type"] == "Group":
            uri = grantee.get("URI", "")
            if uri.endswith("/AllUsers") or uri.endswith("/AuthenticatedUsers"):
                return True
    return False

def check_bucket_policy(bucket):
    try:
        s3.get_bucket_policy(Bucket=bucket)
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchBucketPolicy":
            return False
        raise

for bucket in s3.list_buckets()["Buckets"]:
    name = bucket["Name"]

    bpa_public = check_public_access_block(name)
    acl_public = check_bucket_acl(name)
    policy_public = check_bucket_policy(name)

    print(f"\nBucket: {name}")

    if bpa_public or acl_public or policy_public:
        print(" Potential public exposure")
        if bpa_public:
            print(" - Public Access Block is not fully restrictive")
        if acl_public:
            print(" - Public ACL detected")
        if policy_public:
            print(" - Bucket policy exists (manual inspection required)")
    else:
        print("Bucket is not publicly accessible")