from aws_cdk import ( # type: ignore
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_lambda as _lambda,
    aws_events as events,
    aws_events_targets as targets,
    aws_s3 as s3,
    core,
)

class ScheduledEc2Stack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create an S3 bucket for storing files
        bucket = s3.Bucket(self, "MyBucket")

        # Define the Lambda function
        lambda_function = _lambda.Function(
            self, "MyFunction",
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler="lambda_function.handler",
            code=_lambda.Code.from_inline(
                """
import boto3

def handler(event, context):
    ec2 = boto3.client('ec2')
    ec2.run_instances(
        ImageId='ami-12345678',  # Replace with your AMI ID
        InstanceType='t2.micro',
        KeyName='my-key-pair',  # Replace with your key pair name
        MinCount=1,
        MaxCount=1,
        UserData='''#!/bin/bash
        yum update -y
        yum install -y python3
        yum install -y git
        cd /home/ec2-user/
        git clone https://github.com/djschlicht/force-backup-automator.git     
        cd force-backup-automator
        python3 setup.py install
        python3 force-backup-automator/downloadChromedriver.py
        python3 main.py
        shutdown -h now
        '''
    )
                """
            ),
            role=iam.Role(
                self, 'LambdaExecutionRole',
                assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'),
                managed_policies=[
                    iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSLambdaBasicExecutionRole'),
                    iam.ManagedPolicy.from_aws_managed_policy_name('AmazonEC2FullAccess')
                ]
            )
        )

        # Define the EventBridge rule
        rule = events.Rule(
            self, "Rule",
            schedule=events.Schedule.rate(core.Duration.days(7))
        )

        rule.add_target(targets.LambdaFunction(lambda_function))


app = core.App()
ScheduledEc2Stack(app, "ScheduledEc2Stack")
app.synth()
