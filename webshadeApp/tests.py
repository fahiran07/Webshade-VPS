import random
import time
import uuid
import requests
import traceback
from datetime import datetime
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver

def get_verification_code():
    proxy = "p.webshare.io:9999"
    options = Options()
    # options.add_argument("--headless=new")  # Run in headless mode
    # options.add_argument("--disable-gpu")  # Disable GPU rendering
    options.add_argument(f'--proxy-server={proxy}')
    options.add_argument("--no-sandbox")  # Bypass OS security model
    options.add_argument("--disable-dev-shm-usage")  # Overcome limited resources in containerized environments
    options.add_argument("--log-level=3")  # Reduce logging
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://web.whatsapp.com")      
    driver.quit()
get_verification_code()