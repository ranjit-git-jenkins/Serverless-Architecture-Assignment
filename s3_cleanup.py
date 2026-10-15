"""Lambda: delete objects older than 30 days in a configured bucket (dry-run default)."""
import os
from datetime import datetime, timedelta, timezone
import boto3

def lambda_handler(event, context):
    bucket = os.environ['BUCKET_NAME']
    dry_run = os.environ.get('DRY_RUN', 'true').lower() != 'false'
    cutoff = datetime.now(timezone.utc) - timedelta(days=30)
    s3 = boto3.client('s3')
    old = []
    for page in s3.get_paginator('list_objects_v2').paginate(Bucket=bucket):
        for obj in page.get('Contents', []):
            if obj['LastModified'] < cutoff:
                old.append({'Key': obj['Key']})
    if not dry_run:
        for n in range(0, len(old), 1000):
            s3.delete_objects(Bucket=bucket, Delete={'Objects': old[n:n+1000], 'Quiet': True})
    result = {'bucket': bucket, 'dry_run': dry_run, 'matching_keys': [x['Key'] for x in old]}
    print(result)
    return result
