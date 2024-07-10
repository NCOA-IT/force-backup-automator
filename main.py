from force_backup_automator import BackupController
import subprocess
import datetime

backup_instance = BackupController(driver_location='./chromedriver',
                                   org_link='ORG MAIN URL',
                                   is_headless=0)

secret_name=''
region_name='us-east-1'

creds = backup_instance.get_aws_credentials(secret_name, region_name)

#ORG URL/lightning/setup/DataManagementExport/home',
backup_instance.download_backups(download_location='TARGET LOCATION',
                                 backup_url=creds['backup_url'],
                                 user_name=creds['username'],
                                 password=creds['password'],
                                 bucket=creds['bucket'],
                                 date=datetime.now(),
                                 org_name=creds['org_name'])

# use subprocess to issue shutdown command
subprocess.run("shutdown")
