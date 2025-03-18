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
print("🔧 Setting up Chrome options...")
options = Options()
options.add_argument("--disable-usb-keyboard-detect")
options.add_argument("--disable-features=WebML")

# Initialize the driver
print("🚀 Initializing Chrome WebDriver...")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Define URL
url = 'https://et7india.com/#/login'
print(f"🌐 Opening URL: {url}")
driver.get(url)

# Wait setup
wait = WebDriverWait(driver, 25)

# Login inputs
print("⌛ Waiting for login inputs...")
inputs = wait.until(EC.visibility_of_all_elements_located((By.TAG_NAME, 'input')))
print("✅ Login input fields found.")

# Enter login details
print("📝 Entering login credentials...")
inputs[0].send_keys('9864301450')
inputs[1].send_keys('webshade124432')
print("🔒 Credentials entered.")

# Click login
print("🖱️ Clicking login button...")
login_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'login_btn')))
login_button.click()
print("✅ Login button clicked.")

# Close pop-up
print("📢 Waiting for and closing popup...")
button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[.//div//span[text()='Close']]")))
button.click()
print("❌ Popup closed.")

# Start task
print("🎯 Starting task...")
button = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "startTaskBtn")))
driver.execute_script("arguments[0].scrollIntoView();", button)
button.click()
driver.implicitly_wait(5)
print("✅ Task started.")

# Store scraped data
scraped_data = []

# Function to extract data from one page
index = 1
def extract_cards(index):
    print("🔍 Extracting data from current page...")
    account_cards = driver.find_elements(By.CLASS_NAME, "account_item")
    print(f"📦 Found {len(account_cards)} account cards.")

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

        print(f"📲 Serial: {index}, Number: {number}, Status: {status}, Time: {total_hours}h")

        scraped_data.append({
            'serial': index,
            'number': number,
            'status': status,
            'hours': total_hours
        })
        index += 1
    return len(account_cards)

# Extract all pages
while True:
    card_count = extract_cards(index)
    index += 8

    try:
        print("➡️ Checking for next page...")
        next_button = driver.find_element(By.CLASS_NAME, "nextdata")
        if not next_button.is_enabled():
            print("🛑 Next button disabled. Ending extraction.")
            break
        print("🖱️ Clicking next page button...")
        next_button.click()
        time.sleep(5)

        if card_count < 8:
            print("📉 Less than 8 cards found. Assuming last page.")
            break
    except Exception as e:
        print(f"❗ Exception or no more pages: {e}")
        break

# Close browser
driver.quit()
print("🧹 Browser closed.")

if scraped_data:  # Save only if data exists
    try:
        with open('scraped_data.json', 'w') as f:
            json.dump(scraped_data, f, indent=4)
    except Exception:
        pass  # Ignore error silently