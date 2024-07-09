from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from urllib.parse import unquote
from botocore.exceptions import NoCredentialsError
import re
import time
import requests
import boto3

class BackupController:
    def __init__(self,driver_location,org_link,login_url="https://login.salesforce.com/",is_headless=1,implicit_wait=30):
        self.login_url = login_url
        self.org_link=org_link
        options = webdriver.ChromeOptions()
        if is_headless:
            options.add_argument("--headless")
        self.driver = webdriver.Chrome(driver_location, options=options)
        self.driver.implicitly_wait(implicit_wait)
    
    def login(self,user_name,password):
        login_url=f'{self.login_url}/?un={user_name}&pw={password}'
        self.driver.get(login_url)
    
    def detect_lightning(self,timeout):
        try:
            WebDriverWait(self.driver, timeout).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,"//div[contains(@class,'iframe-parent')]/iframe")))
            print('Lightning Detected')
            return 1
        except TimeoutException:
            print("Classic Detected")
            return 0
    
    def extract_file_info(self,link):
        if self.is_lightning:
            link=unquote(link)
            extract_link = re.search(r'srcUp\(\'(.*?)\'\)',link)
            link= extract_link.group(1)
        
        extract_file_name = re.search(r'fileName=(.*?)&id',link)
        file_name= extract_file_name.group(1)
        return link,file_name

    def download_file(self,url,cookies,file_name,download_location):

        with requests.get(url, stream=True, cookies=cookies) as r:
            r.raise_for_status()
            with open(download_location+file_name, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): 
                    # If you have chunk encoded response uncomment if
                    # and set chunk_size parameter to None.
                    #if chunk: 
                    f.write(chunk)
    
    def upload_to_s3(file_name, bucket, org_name, date, object_name=None):
        """
        Upload a file to an S3 bucket.
    
        :param file_name: File to upload
        :param bucket: Bucket to upload to
        :param org_name: Salesforce Organization name
        :param object_name: S3 object name. If not specified then file_name is used
        :return: True if file was uploaded, else False
        """
        # If S3 object_name was not specified, use file_name
        if object_name is None:
            object_name = file_name
    
        # Upload the file
        s3_client = boto3.client('s3')
        try:
            fp = f'{bucket}/{org_name}/{date}'
            s3_client.upload_file(file_name, fp, object_name)
        except FileNotFoundError:
            print("The file was not found")
            return False
        except NoCredentialsError:
            print("Credentials not available")
            return False
        return True        
        
    def download_backups(self,download_location,backup_url,bucket,date,
                         cookies=None,user_name=None,password=None,org_name=None):
        
        if cookies is None:
            if (user_name is not None and password is not None):
                print('Logging in')
                self.login(user_name,password)
                print('Logged in')
            else:
                raise ValueError("Username and Password Argument is Missing")
        print('Navigate to Backup URL')
        self.driver.get(backup_url)
        time.sleep(5) ## wait 5 seconds
        timeout=5 
        self.is_lightning=self.detect_lightning(timeout) ##check lightning experience

        soup=BeautifulSoup(self.driver.page_source, 'lxml') ##prepare the source

        if cookies is None:
            cookies = {'oid': self.driver.get_cookie("oid")["value"], 'sid':self.driver.get_cookie("sid")["value"]}
        print('Reading file links')
        for link in soup.find_all('a', text='download'):
            file_path,file_name = self.extract_file_info(link["href"])
            file_url= self.org_link+file_path
            print('Downloading file '+file_url)
            self.download_file(file_url,cookies,file_name,download_location)
            self.upload_to_s3(f'{download_location}/{file_name}', bucket, org_name, date)
        
        self.driver.quit()

        
    
    

        

            
