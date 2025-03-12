from celery import shared_task, states
from django.http import JsonResponse
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
from faker import Faker
from webshadeApp.models import whatsappConnection,ChromeInstance
from webshadeApp.functions import send_telegram_message

fake = Faker()

# Function to simulate typing
def random_sleep(min_time, max_time):
    time.sleep(random.uniform(min_time, max_time))

def simulate_typing(element, text, typing_speed=0.02):
    for char in text:
        element.send_keys(char)
        random_sleep(typing_speed, typing_speed + 0.03)

@shared_task(bind=True, max_retries=2)
def get_verification_code(self,whatsapp,connect_id, user_id):
    proxy = "p.webshare.io:9999"
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--log-level=3")
    options.add_argument("--disable-sync")  # Chrome syncing band kare (kam resource use hoga)
    options.add_argument("--window-size=800,600")  # Small window size to reduce memory usage
    options.add_argument("--mute-audio")  # Audio processes ko disable kare
    options.add_argument("--disable-extensions")  # Extensions load na ho

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    pid = driver.service.process.pid
    chrome_instance = ChromeInstance.objects.create(user_id=user_id, pid=pid)
    chrome_instance.save()

    try:
        print('Opening website')
        url = 'https://et7india.com/#/login'
        driver.get(url)
        print('Logging into website')
        wait = WebDriverWait(driver, 40)
        inputs = wait.until(EC.visibility_of_all_elements_located((By.TAG_NAME, 'input')))

        simulate_typing(inputs[0], '9864301450', typing_speed=0.2)
        simulate_typing(inputs[1], 'rahman124432', typing_speed=0.2)

        login_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'login_btn')))
        login_button.click()

        button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[.//div//span[text()='Close']]")))
        button.click()

        button = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "startTaskBtn")))
        driver.execute_script("arguments[0].scrollIntoView();", button)
        button.click()

        button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'switch_button')))
        button.click()

        number_input = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'styled-input')))
        simulate_typing(number_input, whatsapp, typing_speed=0.1)
        print('Getting code')
        button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'getcode')))
        button.click()
        timeout = time.time() + 120  # 2-minute timeout
        while True:
            verification_code_divs = driver.find_elements(By.CSS_SELECTOR, "div.verification_code div.notranslate.input-box")

            if len(verification_code_divs) == 8 and all(div.text.strip() for div in verification_code_divs):
                break  # Exit loop once all boxes are filled with the code
                print('Code got')
            try:
                error_message_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "van-toast__text"))
                )
                error_message = error_message_element.text.strip().lower()

                if error_message and error_message != "please wait":
                    driver.quit()
                    return update_error(error_message,connect_id)

            except:
                pass

            if time.time() > timeout:
                driver.quit()
                return update_error('Timeout: No code appeared',connect_id)

            random_sleep(1, 2)

        verification_code = ''.join([div.text.strip() for div in verification_code_divs])
        print('Code is:',verification_code)

        print('Sending Code')
        code_sending_status = send_code_to_api(verification_code, connect_id)
        if not code_sending_status:
            driver.quit()
            return update_error('Code sending failed.',connect_id)
        print('Code sent succesfully')
        wait_time = 150  # Max wait time
        refresh_interval = 20  # Interval between refresh attempts
        start_time = time.time()
        last_refresh = time.time()
        while time.time() - start_time < wait_time:
            try:
                element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, f"//div[@class='account_status']//div[@class='account' and contains(text(), '{whatsapp}')]"))
                )
                online_status = set_status_online(connect_id)
                print("Online status",online_status)
                if online_status:
                    driver.quit()
                    return True
                driver.quit()
                return update_error('Error while setting whatsapp online.',connect_id)

            except:
                pass

            if time.time() - last_refresh >= refresh_interval:
                print('Clicking refresh')
                try:
                    refresh_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CLASS_NAME, "updateList"))
                    )
                    refresh_button.click()
                    last_refresh = time.time()
                except:
                    traceback.print_exc()

            random_sleep(1, 2)
        driver.quit()
        return update_error("Whatsapp didn't connect",connect_id)

    except Exception as e:
        e = traceback.print_exc()
        driver.quit()
        return update_error(e,connect_id)

    finally:
        driver.quit()

@shared_task
def test_task(message):
    print(f"Received message: {message}")
    return {'status': 'success', 'message': message}


# Helper Functions
def send_code_to_api(code, connect_id):
    url = f"http://82.29.162.97/send-code-backend/?connect-id={connect_id}&code={code}"
    try:
        response = requests.post(url)
        response_data = response.json()
        return response_data.get("status")
    except Exception as e:
        print(f"⚠️ API Error: {e}")
        return False

# Helper Functions
def update_error(error, connect_id):
    url = f"http://82.29.162.97/update-error/?connect-id={connect_id}&error={error}"
    try:
        response = requests.post(url)
        response_data = response.json()
        return response_data.get("status")
    except Exception as e:
        print(f"⚠️ API Error: {e}")
        return False

def set_status_online(connect_id):
    url = f"http://82.29.162.97/set-status-online/?connect-id={connect_id}"
    try:
        response = requests.post(url)
        response_data = response.json()
        print('Returing')
        return response_data.get("status")
    except Exception as e:
        traceback.print_exc()
        return False
