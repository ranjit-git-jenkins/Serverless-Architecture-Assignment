"""Mock-only tests; never contact AWS."""
import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta, timezone

ROOT=Path(__file__).resolve().parents[1] / 'lambda_functions'
def load(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/(name+'.py'))
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod

class Tests(unittest.TestCase):
    @patch('boto3.client')
    def test_ec2_tags(self,client):
        ec2=MagicMock();client.return_value=ec2
        pages=[[{'Reservations':[{'Instances':[{'InstanceId':'i-stop'}]}]}],[{'Reservations':[{'Instances':[{'InstanceId':'i-start'}]}]}]]
        ec2.get_paginator.return_value.paginate.side_effect=pages
        r=load('ec2_tag_manager').lambda_handler({},None)
        self.assertEqual(r,{'stopped':['i-stop'],'started':['i-start']})
        ec2.stop_instances.assert_called_once_with(InstanceIds=['i-stop'])
        ec2.start_instances.assert_called_once_with(InstanceIds=['i-start'])

    @patch('boto3.client')
    @patch.dict('os.environ',{'BUCKET_NAME':'sample-bucket','DRY_RUN':'true'})
    def test_s3_cleanup_dry_run(self,client):
        s3=MagicMock();client.return_value=s3
        now=datetime.now(timezone.utc)
        s3.get_paginator.return_value.paginate.return_value=[{'Contents':[{'Key':'old.txt','LastModified':now-timedelta(days=40)},{'Key':'new.txt','LastModified':now-timedelta(days=1)}]}]
        r=load('s3_cleanup').lambda_handler({},None)
        self.assertEqual(r['matching_keys'],['old.txt'])
        s3.delete_objects.assert_not_called()

    @patch('boto3.client')
    def test_encryption_audit(self,client):
        from botocore.exceptions import ClientError
        s3=MagicMock();client.return_value=s3
        s3.list_buckets.return_value={'Buckets':[{'Name':'a'},{'Name':'b'}]}
        s3.get_bucket_encryption.side_effect=[{},ClientError({'Error':{'Code':'ServerSideEncryptionConfigurationNotFoundError','Message':'missing'}},'GetBucketEncryption')]
        r=load('s3_encryption_audit').lambda_handler({},None)
        self.assertEqual(r['without_explicit_encryption_rule'],['b'])

    @patch('boto3.client')
    def test_auto_tag(self,client):
        ec2=MagicMock();client.return_value=ec2
        event={'source':'aws.ec2','detail-type':'EC2 Instance State-change Notification','detail':{'instance-id':'i-example','state':'running'}}
        r=load('ec2_auto_tag').lambda_handler(event,None)
        self.assertEqual(r['instance_id'],'i-example')
        ec2.create_tags.assert_called_once()
        self.assertTrue(load('ec2_auto_tag').lambda_handler({},None)['skipped'])

if __name__=='__main__': unittest.main()
