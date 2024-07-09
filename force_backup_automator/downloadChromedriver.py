import os
import requests
import zipfile
import platform
from bs4 import BeautifulSoup

def get_latest_chromedriver_version():
    url = "https://sites.google.com/chromium.org/driver/downloads"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    version_tag = soup.find('a', href=True, text=lambda x: x and "ChromeDriver" in x)
    latest_version = version_tag.text.split()[-1]
    return latest_version

def download_chromedriver(version, os_type):
    base_url = f"https://chromedriver.storage.googleapis.com/{version}/chromedriver_{os_type}.zip"
    response = requests.get(base_url, stream=True)
    zip_path = f"chromedriver_{os_type}.zip"
    
    with open(zip_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(".")
    
    os.remove(zip_path)
    print(f"ChromeDriver {version} downloaded and extracted successfully.")

def main():
    os_type_map = {
        'Windows': 'win32',
        'Darwin': 'mac64',
        'Linux': 'linux64'
    }
    
    system = platform.system()
    os_type = os_type_map.get(system, None)
    
    if not os_type:
        print(f"Unsupported OS: {system}")
        return
    
    version = get_latest_chromedriver_version()
    print(f"Latest ChromeDriver version: {version}")
    download_chromedriver(version, os_type)

if __name__ == "__main__":
    main()
