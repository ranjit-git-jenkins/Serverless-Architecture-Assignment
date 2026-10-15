"""Lambda: add launch date and management tag on EC2 running state event."""
from datetime import datetime, timezone
import boto3

def lambda_handler(event, context):
    detail = event.get('detail', {})
    instance_id = detail.get('instance-id')
    state = detail.get('state')
    if event.get('source') != 'aws.ec2' or event.get('detail-type') != 'EC2 Instance State-change Notification' or state != 'running' or not instance_id:
        return {'skipped': True, 'reason': 'Not an EC2 running event'}
    today = datetime.now(timezone.utc).date().isoformat()
    boto3.client('ec2').create_tags(Resources=[instance_id], Tags=[{'Key': 'LaunchDate', 'Value': today}, {'Key': 'ManagedBy', 'Value': 'Lambda'}])
    result = {'instance_id': instance_id, 'LaunchDate': today, 'ManagedBy': 'Lambda'}
    print(result)
    return result
