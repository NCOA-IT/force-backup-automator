from force-backup-automator import BackupController
import boto3
import subprocess

# download chromedriver from web

# use secrets manager to get salesforce credentials

backup_instance = BackupController(driver_location='./chromedriver',
                                   org_link='ORG MAIN URL',
                                   is_headless=0)

# modify download_backups to upload completed file to s3 bucket s3://ORGNAME/DATE/
backup_instance.download_backups(download_location='TARGET LOCATION',
                                 backup_url='ORG URL/lightning/setup/DataManagementExport/home',
                                 user_name='USERNAME',
                                 password='PASSWORD')

# use subprocess to issue shutdown command
subprocess.run("shutdown")
