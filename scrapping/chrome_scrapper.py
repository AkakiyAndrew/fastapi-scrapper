# from asyncio import Queue
# import asyncio
import chromedriver
import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from chromedriver import check_driver

HEADLESS_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}

def get_driver():
    # options for headless scrapping, so that services wouldn't block the request
    options = webdriver.ChromeOptions()
    # options.add_argument("--incognito")
    options.add_experimental_option("excludeSwitches", ['enable-automation'])
    options.add_argument('--headless=new')
    options.add_argument(f"user-agent={HEADLESS_HEADERS['User-Agent']}")
    options.add_argument('--disable-blink-features=AutomationControlled')

    # TODO: use pathlib
    driver_dir_path = os.path.abspath("driver")
    check_driver(driver_dir_path)

    driver_abs_path = os.path.join(driver_dir_path, "chromedriver")
    if sys.platform.startswith('win32'):
        driver_abs_path += ".exe" 

    s = Service(driver_abs_path)  # Нужен путь к установленному ChromeDriver
    driver = webdriver.Chrome(service=s, options=options)
    return driver

# Selenium-based scrapper, to be used for scrapping pages
# TODO: async queue for urls?
# TODO: make as singleton, and/or with limited time of driver life after last usage
class ChromeScrapper:
    # queue = Queue()

    def __init__(self):
        self.driver = get_driver()

    def get_body(self, url) -> str:
        self.driver.get(url)
        body = self.driver.page_source
        
        return body
    
# TODO: apply
# import os
# import sys
# import asyncio
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service

# def get_driver():
#     driver_dir_path = os.path.abspath("driver")
#     check_driver(driver_dir_path)

#     driver_abs_path = os.path.join(driver_dir_path, "chromedriver")
#     if sys.platform.startswith('win32'):
#         driver_abs_path += ".exe" 

#     s = Service(driver_abs_path)
#     driver = webdriver.Chrome(service=s, options=options)
#     return driver

# class ChromeScrapper:
#     def __init__(self, timeout=300):
#         self.driver = None
#         self.timeout = timeout
#         self.timer = None
#         self.lock = asyncio.Lock()

#     async def start_driver(self):
#         async with self.lock:
#             if self.driver is None:
#                 self.driver = get_driver()
#             await self.reset_timer()

#     async def stop_driver(self):
#         async with self.lock:
#             if self.driver is not None:
#                 self.driver.quit()
#                 self.driver = None

#     async def reset_timer(self):
#         if self.timer is not None:
#             self.timer.cancel()
#         self.timer = asyncio.get_event_loop().call_later(self.timeout, asyncio.create_task, self.stop_driver())

#     async def get_body(self, url) -> str:
#         await self.start_driver()
#         self.driver.get(url)
#         body = self.driver.page_source
#         await self.reset_timer()
#         return body