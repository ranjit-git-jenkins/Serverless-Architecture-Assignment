"""Lambda: stop Action=Auto-Stop and start Action=Auto-Start EC2 instances."""
import boto3

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    result = {'stopped': [], 'started': []}
    for tag, state, action, target in [('Auto-Stop', 'running', ec2.stop_instances, 'stopped'), ('Auto-Start', 'stopped', ec2.start_instances, 'started')]:
        paginator = ec2.get_paginator('describe_instances')
        ids = []
        for page in paginator.paginate(Filters=[{'Name': 'tag:Action', 'Values': [tag]}, {'Name': 'instance-state-name', 'Values': [state]}]):
            ids.extend(i['InstanceId'] for r in page['Reservations'] for i in r['Instances'])
        for pos in range(0, len(ids), 100):
            batch = ids[pos:pos + 100]
            if batch:
                action(InstanceIds=batch)
                result[target].extend(batch)
    print(result)
    return result
