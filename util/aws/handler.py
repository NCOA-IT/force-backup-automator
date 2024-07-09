import boto3

def handler(event, context):
    # use SecretsManager to get AMI and key/pair
    ec2 = boto3.client('ec2')
    ec2.run_instances(
        ImageId='ami-12345678',  # Replace with your AMI ID
        InstanceType='t2.micro',
        KeyName='my-key-pair',  # Replace with your key pair name
        MinCount=1,
        MaxCount=1,
        UserData="""
          #!/bin/bash
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
          """
    )
