# Graded Assignment on Serverless Architecture — Four AWS Lambda/Boto3 Tasks

**Student repository:** replace `YOUR-USERNAME` with your GitHub username after uploading.

## Selected tasks
1. EC2 Auto-Stop / Auto-Start based on `Action` tags (`lambda_functions/ec2_tag_manager.py`).
2. Delete S3 objects older than 30 days (`lambda_functions/s3_cleanup.py`). **DRY_RUN=true by default**; set false only in a dedicated test bucket.
3. Audit S3 buckets lacking an explicit default encryption rule (`lambda_functions/s3_encryption_audit.py`). AWS S3 encrypts all new objects by default, so a missing rule does not mean stored objects are unencrypted.
5. Auto-tag EC2 instances when they enter the running state (`lambda_functions/ec2_auto_tag.py`). The event approximates launch and also fires on restarts; for launch-only behavior add lifecycle filtering or a tag-existence check.

## Local tests (no AWS account required)
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python -m unittest discover -s tests -v
```
Tests mock AWS clients. Passing local tests does **not** prove Lambda or AWS integration worked.

## AWS deployment steps (when access is restored)
1. Create Lambda execution roles with AWSLambdaBasicExecutionRole and the relevant IAM example in `iam/`. Restrict wildcard resources wherever the action permits, and scope EC2 modifications to tagged resources.
2. Create four Lambda functions with Python runtime and paste each corresponding Python file as `lambda_function.py`; handler `lambda_function.lambda_handler`.
3. EC2 tag manager: create two test instances, `Action=Auto-Stop` and `Action=Auto-Start`; invoke manually and check state transitions.
4. S3 cleanup: create dedicated bucket; set `BUCKET_NAME` and initially `DRY_RUN=true`. Note S3 LastModified is controlled by S3, not by changing your laptop clock. Use fixture/mocks for historical timestamps or wait for aged objects. After confirming selection, optionally test with `DRY_RUN=false` in a disposable bucket.
5. Encryption audit: create/inspect buckets and invoke; review CloudWatch Logs. Missing explicit encryption config does not imply unencrypted objects.
6. EC2 auto-tag: create EventBridge rule matching source `aws.ec2`, detail-type `EC2 Instance State-change Notification`, detail state `running`; target the auto-tag Lambda. Launch an instance and verify tags.
7. Save genuine AWS console and CloudWatch screenshots **only after** real AWS tests.

## IAM note
Example IAM files are starting points and may need account-specific adjustments. Attach Lambda logging permissions separately. Do not use AmazonEC2FullAccess or AmazonS3FullAccess in production.

## Status
AWS console access is unavailable. This repository contains deployment-ready example code, mocked local tests, and documentation; it does **not** represent a live deployed Lambda solution. No AWS screenshots are claimed.
