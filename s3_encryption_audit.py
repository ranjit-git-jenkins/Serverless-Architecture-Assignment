"""Lambda: report buckets without an explicit default encryption configuration.
Note: S3 automatically encrypts new objects with SSE-S3; lack of a bucket rule
is not evidence of unencrypted stored objects.
"""
import boto3
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    without_explicit_rule = []
    errors = []
    for bucket in s3.list_buckets().get('Buckets', []):
        name = bucket['Name']
        try:
            s3.get_bucket_encryption(Bucket=name)
        except ClientError as exc:
            code = exc.response.get('Error', {}).get('Code', '')
            if code in ('ServerSideEncryptionConfigurationNotFoundError', '404'):
                without_explicit_rule.append(name)
            else:
                errors.append({'bucket': name, 'error': code})
    result = {'without_explicit_encryption_rule': without_explicit_rule, 'errors': errors}
    print(result)
    return result
