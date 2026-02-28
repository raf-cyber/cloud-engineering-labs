import boto3
from datetime import datetime, timedelta, timezone

REGION = "us-west-1"
STOPPED_TAG_KEY = "stopped_at"
PROTECTED_TAG_KEY = "protected"
DRY_RUN = True  

ec2 = boto3.resource("ec2", region_name=REGION)
now = datetime.now(timezone.utc)

def get_tag_value(tags, key):
    if not tags:
        return None
    for tag in tags:
        if tag["Key"] == key:
            return tag["Value"]
    return None

print("Scanning EC2 instances...\n")

for instance in ec2.instances.all():
    instance_id = instance.id
    state = instance.state["Name"]
    tags = instance.tags or []

    protected = get_tag_value(tags, PROTECTED_TAG_KEY) == "true"
    stopped_at_value = get_tag_value(tags, STOPPED_TAG_KEY)

    print(f"Instance {instance_id} | state={state}")

    
    if protected:
        print("  -> Skipped (protected=true)\n")
        continue

    
    if state == "running":
        if stopped_at_value:
            instance.delete_tags(Tags=[{"Key": STOPPED_TAG_KEY}])
            print("  -> Running again, removed stopped_at tag\n")
        else:
            print("  -> Running\n")
        continue

    
    if state == "stopped" and not stopped_at_value:
        instance.create_tags(
            Tags=[{"Key": STOPPED_TAG_KEY, "Value": now.isoformat()}]
        )
        print("  -> Stopped detected, tagged stopped_at\n")
        continue

    
    if state == "stopped" and stopped_at_value:
        stopped_at = datetime.fromisoformat(stopped_at_value)
        stopped_duration = now - stopped_at

        if stopped_duration >= timedelta(days=7):
            if DRY_RUN:
                print(
                    f"  -> DRY RUN: would delete (stopped {stopped_duration.days} days)\n"
                )
            else:
               
                print("  -> TERMINATED\n")
        else:
            print(
                f"  -> Stopped {stopped_duration.days} days (below threshold)\n"
            )