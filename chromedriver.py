import os
from pathlib import Path
import shutil
import requests
import subprocess
import wget
import zipfile
import sys

# TODO: logging
# TODO: use pathlib

def download_latest_version(version_number, download_url, driver_directory):
    """Download latest version of chromedriver to a specified directory.
    :param driver_directory: Directory to save and download chromedriver files into.
    :type driver_directory: str
    :param version_number: Latest online chromedriver release from chromedriver.storage.googleapis.com.
    :type version_number: str
    :return: None
    """
    print("Attempting to download latest available driver ......")
    print(download_url)
    # Download driver as a zip file to specified folder
    latest_driver_zip = wget.download(download_url, out=driver_directory)
    # Read zip file
    with zipfile.ZipFile(latest_driver_zip, 'r') as downloaded_zip:
         for f in downloaded_zip.namelist():
            if '/chromedriver' not in f:
                continue

            source = downloaded_zip.open(f)
            target = open(Path(driver_directory) / Path(f).name, "wb")
            
            with source, target:
                shutil.copyfileobj(source, target)

        # Extract contents from downloaded zip file to specified folder path
        # downloaded_zip.extractall(path=driver_directory)
    print(f"\nSuccessfully downloaded chromedriver version {version_number} to:\n{driver_directory}")
    # Delete the zip file downloaded
    os.remove(latest_driver_zip)
    return


def check_driver(driver_directory):
    """Check local chromedriver version and compare it with latest available version online.
    :param driver_directory: Directory to store chromedriver executable.
    Required to add driver_directory to path before using.
    :type driver_directory: str
    :return: True if chromedriver executable is already in driver_directory, else it is automatically downloaded.
    """
    os_name = obtain_os()
    online_driver_version, download_url = get_latest_chromedriver_release(os_name)
    try:
        # Executes cmd line entry to check for existing web-driver version locally
        if not os.path.exists(driver_directory):
            os.mkdir(driver_directory)
        os.listdir()
        driver_abs_path = os.path.join(os.path.abspath(driver_directory), "chromedriver")
        if os_name == "win64":
            driver_abs_path += ".exe"

        cmd_run = subprocess.run([driver_abs_path, "--version"], capture_output=True, text=True)
    except FileNotFoundError:
        # Handling case if chromedriver not found in path
        print("No chromedriver executable found in specified path\n")
        download_latest_version(online_driver_version, download_url, driver_directory)
    else:
        # Extract local driver version number as string from terminal output
        local_driver_version = cmd_run.stdout.split()[1]
        if os_name.startswith("linux"):
            chrome_version = subprocess.run(["google-chrome", "--version"], capture_output=True, text=True).stdout.split()[2]
        else:
            chrome_version = subprocess.getoutput('reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v version').split()[-1]
        print(f"Local browser version: {chrome_version}")
        print(f"Local chromedriver version: {local_driver_version}")
        print(f"Latest online chromedriver version: {online_driver_version}")
        
        if local_driver_version == online_driver_version or chrome_version == local_driver_version:
            return True
        else:
            download_latest_version(online_driver_version, download_url, driver_directory)


def get_latest_chromedriver_release(os_name):
    """ Check for latest chromedriver release version online"""
    latest_release_url = "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json"
    response = requests.get(latest_release_url)
    data = response.json()
    online_driver_version = data['channels']['Stable']['version']
    latest_downloads = data['channels']['Stable']['downloads']['chromedriver']
    download_url = None

    for platform in latest_downloads:
        if platform['platform'] == os_name:
            download_url = platform['url']
    return online_driver_version, download_url


def obtain_os():
    """Obtains operating system based on chromedriver supported by from https://chromedriver.chromium.org/
    :return: str"""
    if sys.platform.startswith('win32'):
        os_name = 'win64'
    elif sys.platform.startswith('linux'):
        os_name = 'linux64'
    elif sys.platform.startswith('darwin'):
        os_name = 'mac64'
    return os_name
