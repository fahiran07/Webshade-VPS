from celery import shared_task, states
from django.http import JsonResponse
import random
import time
import redis
import os
import uuid
import requests
import traceback
import tempfile
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from faker import Faker
from webshadeApp.models import whatsappConnection
from webshadeApp.functions import send_telegram_message


fake = Faker()

# Function to simulate typing
def random_sleep(min_time, max_time):
    time.sleep(random.uniform(min_time, max_time))

@shared_task(ignore_result=True,max_retries=0)
def get_verification_code(whatsapp,connect_id, user_id):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--mute-audio")  # Audio processes ko disable kare
    options.add_argument("--disable-extensions")  # Extensions load na ho
    options.add_argument("--disable-background-timer-throttling")
    options.add_argument("--disable-backgrounding-occluded-windows")
    options.add_argument("--incognito")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36")
    temp_dir = f"/tmp/chrome_{os.getpid()}_{tempfile.mktemp()}"
    options.add_argument(f"--user-data-dir={temp_dir}")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        print('Opening website')
        url = 'https://et7india.com/#/login'
        driver.get(url)
        print('Logging into website')
        wait = WebDriverWait(driver, 20)
        inputs = wait.until(EC.visibility_of_all_elements_located((By.TAG_NAME, 'input')))
        numbers = ['6000694134']
        inputs[0].send_keys(random.choice(numbers))
        inputs[1].send_keys('webshade124432')
        print('Page URL:', driver.current_url)
        login_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'login_btn')))
        login_button.click()
        try:
            error_message_element = WebDriverWait(driver, 25).until(EC.presence_of_element_located((By.CLASS_NAME, "van-toast__text")))
            print("This is error message:",error_message_element.text.strip().lower())
        except Exception as e:
            print('Toast element not found')

        try:
            error_message_element = WebDriverWait(driver, 25).until(EC.presence_of_element_located((By.CLASS_NAME, "van-toast__text")))
            print("This is error message:",error_message_element.text.strip().lower())
            button = WebDriverWait(driver,50).until(EC.element_to_be_clickable((By.XPATH, "//button[.//div//span[text()='Close']]")))
            button.click()
            print('Page URL:', driver.current_url)
        except:
            status = update_error('Unable to execute, Please try again',connect_id,pid)
            print('Page URL:', driver.current_url)
            return status

        button = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "startTaskBtn")))
        driver.execute_script("arguments[0].scrollIntoView();", button)
        button.click()
        print('Page URL:', driver.current_url)
        print('Start button clicked')

        

        button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'switch_button')))
        button.click()
        # Check the innerHTML of the button
        print('Page URL:', driver.current_url)
        print('this is button',button.get_attribute("innerHTML").strip().lower())
        if button.get_attribute("innerHTML").strip().lower() == "add":
            button.click()
        else:
            print("Button text is not 'add', skipping click.")

        number_input = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'styled-input')))
        number_input.send_keys(whatsapp)
        print('Getting code')
        button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "getcode")))
        button.click()
        timeout = time.time() + 120  # 2-minute timeout
        while True:
            verification_code_divs = driver.find_elements(By.CSS_SELECTOR, "div.verification_code div.notranslate.input-box")

            if len(verification_code_divs) == 8 and all(div.text.strip() for div in verification_code_divs):
                break  # Exit loop once all boxes are filled with the code
                print('Code got')
            try:
                error_message_element = WebDriverWait(driver, 25).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "van-toast__text"))
                )
                error_message = error_message_element.text.strip().lower()

                if error_message and error_message != "please wait":
                    status = update_error(f'{error_message} - Error',connect_id,pid)
                    return status

            except:
                pass

            if time.time() > timeout:
                status = update_error('Timeout: No code appeared',connect_id,pid)
                return status

            random_sleep(1, 2)

        verification_code = ''.join([div.text.strip() for div in verification_code_divs])
        print('Code is:',verification_code)

        print('Sending Code')
        code_sending_status = send_code_to_api(verification_code, connect_id)
        if not code_sending_status:
            status = update_error('Code sending failed.',connect_id,pid)
            return status
        print('Code sent succesfully')
        try:
            # Wait for the element with the given number to appear
            element = WebDriverWait(driver, 120).until(
                EC.presence_of_element_located((By.XPATH, f"//div[@class='account_status']//div[@class='account' and contains(text(), '{whatsapp}')]"))
            )
            print('Verifying')
            if element:
                # If element is found, set status online
                online_status = set_status_online(connect_id)
                print("Online status:", online_status)
                if online_status:
                    return True
                else:
                    return update_error("Error while setting WhatsApp online.", connect_id, pid)
    
        except Exception as e:
            print(f"Error: {e}")

        # If element is not found or any error occurs
        return update_error("WhatsApp didn't connect", connect_id, pid)

    except Exception as e:
        traceback.print_exc()
        driver.quit()
        status = update_error(e,connect_id,pid)
        return status

    finally:
        driver.quit()

@shared_task
def test_task(message):
    print(f"Received message: {message}")
    return {'status': 'success', 'message': message}


# Helper Functions
def send_code_to_api(code, connect_id):
    url = f"https://webshade.site/send-code-backend/?connect-id={connect_id}&code={code}"
    try:
        response = requests.post(url)
        response_data = response.json()
        return response_data.get("status")
    except Exception as e:
        print(f"⚠️ API Error: {e}")
        return False

# Helper Functions
def update_error(error, connect_id,pid):
    url = f"https://webshade.site/update-error/?connect-id={connect_id}&error={error}&pid={pid}"
    try:
        response = requests.post(url)
        response_data = response.json()
        return response_data.get("status")
    except Exception as e:
        print(f"⚠️ API Error: {e}")
        return False

def set_status_online(connect_id):
    url = f"https://webshade.site/set-status-online/?connect-id={connect_id}"
    try:
        response = requests.post(url)
        response_data = response.json()
        print('Returing')
        return response_data.get("status")
    except Exception as e:
        traceback.print_exc()
        return False
