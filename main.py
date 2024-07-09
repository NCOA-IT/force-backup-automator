from force-backup-automator import BackupController
from botocore.exceptions import NoCredentialsError, ClientError
import boto3
import json
import subprocess
import datetime

creds = get_aws_credentials(secret_name, region_name)

backup_instance = BackupController(driver_location='./chromedriver',
                                   org_link='ORG MAIN URL',
                                   is_headless=0)

backup_instance.download_backups(download_location='TARGET LOCATION',
                                 backup_url='ORG URL/lightning/setup/DataManagementExport/home',
                                 user_name='USERNAME',
                                 password='PASSWORD',
                                 bucket='',
                                 date=datetime.now(),
                                 org_name=org_name)

# use subprocess to issue shutdown command
subprocess.run("shutdown")
