from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import re
import time
import os
import json

# Setup Chrome options
options = Options()
options.add_argument("--disable-usb-keyboard-detect")
options.add_argument("--disable-features=WebML")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Define URL
host_phone = '8822919998'
url = 'https://et7india.com/#/login'
driver.get(url)

# Wait setup
wait = WebDriverWait(driver, 50)

# Login inputs
inputs = wait.until(EC.visibility_of_all_elements_located((By.TAG_NAME, 'input')))

# Enter login details
inputs[0].send_keys(host_phone)
inputs[1].send_keys('Taniya124432')

# Click login
login_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'login_btn')))
login_button.click()

# Close pop-up
button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[.//div//span[text()='Close']]")))
button.click()

time.sleep(10)
# Start task
button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "startTaskBtn")))
driver.execute_script("arguments[0].scrollIntoView();", button)
button.click()
driver.implicitly_wait(5)

# Store scraped data
scraped_data = []

# Function to extract data from one page
index = 1
def extract_cards(index):
    account_cards = driver.find_elements(By.CLASS_NAME, "account_item")

    for card in account_cards:
        number = card.find_element(By.CLASS_NAME, "account").text
        status = card.find_element(By.CLASS_NAME, "status").text
        time_len = card.find_element(By.CLASS_NAME, "timelen").text

        # Extract days, hours, minutes
        days = re.search(r"(\d+)d", time_len)
        hours = re.search(r"(\d+)h", time_len)
        minutes = re.search(r"(\d+)m", time_len)

        # Calculate total hours
        total_hours = (int(days.group(1)) * 24 if days else 0) + \
                      (int(hours.group(1)) if hours else 0) + \
                      (int(minutes.group(1)) // 60 if minutes else 0)


        scraped_data.append({
            'serial': index,
            'number': number,
            'status': status,
            'hours': total_hours,
            'host_phone':host_phone
        })
        index += 1
    return len(account_cards)

# Extract all pages
while True:
    card_count = extract_cards(index)
    index += 8

    try:
        next_button = driver.find_element(By.CLASS_NAME, "nextdata")
        if not next_button.is_enabled():
            print("🛑 Next button disabled. Ending extraction.")
            break
        next_button.click()
        time.sleep(3)

        if card_count < 8:
            break
    except Exception as e:
        break

# Close browser
driver.quit()

if scraped_data:  # Save only if data exists
    try:
        with open('scraped_data.json', 'w') as f:
            json.dump(scraped_data, f, indent=4)
    except Exception:
        pass  # Ignore error silently