import boto3
import json
import logging
from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)

REGION = "us-west-2"

iam_client = boto3.client("iam", region_name=REGION)
ses_client = boto3.client("ses", region_name=REGION)


def check_for_wildcard_policy(role_name, policy_name):
    try:
        response = iam_client.get_role_policy(
            RoleName=role_name,
            PolicyName=policy_name
        )

        policy_doc = response["PolicyDocument"]

        for statement in policy_doc.get("Statement", []):
            if statement.get("Effect") != "Allow":
                continue

            actions = statement.get("Action", [])
            resources = statement.get("Resource", [])

            if isinstance(actions, str):
                actions = [actions]
            if isinstance(resources, str):
                resources = [resources]

            for action in actions:
                if "*" in action:
                    logging.warning(
                        f"Wildcard action detected in policy {policy_name} on role {role_name}"
                    )
                    return True

            for resource in resources:
                if "*" in resource:
                    logging.warning(
                        f"Wildcard resource detected in policy {policy_name} on role {role_name}"
                    )
                    return True

        logging.info(
            f"No wildcard permissions found in policy {policy_name} on role {role_name}"
        )
        return False

    except iam_client.exceptions.NoSuchEntityException:
        logging.error("Role or inline policy does not exist")
        return False

    except ClientError as e:
        logging.error(f"AWS error while checking policy: {e}")
        return False


def handle_log_deletion_event(event):
    event_name = event.get("eventName")
    event_source = event.get("eventSource")

    if (
        event_source != "logs.amazonaws.com"
        or event_name not in ["DeleteLogGroup", "DeleteLogStream"]
    ):
        return

    user = event.get("userIdentity", {}).get("arn", "Unknown")
    log_group = event.get("requestParameters", {}).get("logGroupName", "Unknown")
    event_time = event.get("eventTime", "Unknown")

    logging.warning(
        f"CloudWatch Logs deletion detected: {event_name} by {user}"
    )

    try:
        ses_client.send_email(
            Source="system@example.com",
            Destination={
                "ToAddresses": ["recipient@example.com"]
            },
            Message={
                "Subject": {
                    "Data": "SECURITY ALERT: CloudWatch Logs Deleted"
                },
                "Body": {
                    "Text": {
                        "Data": (
                            f"User: {user}\n"
                            f"Action: {event_name}\n"
                            f"Log Group: {log_group}\n"
                            f"Time: {event_time}"
                        )
                    }
                }
            }
        )
    except ClientError as e:
        logging.error(f"Failed to send SES alert: {e}")

    with open("deleted_logs_audit.txt", "a") as f:
        f.write(
            f"{event_time} | {user} | {event_name} | {log_group}\n"
        )


if __name__ == "__main__":
    with open("cloudtrail_event.json") as file:
        cloudtrail_event = json.load(file)

    handle_log_deletion_event(cloudtrail_event)