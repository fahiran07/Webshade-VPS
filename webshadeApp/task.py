from celery import shared_task, states
from django.http import JsonResponse
import random
import time
import redis
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

@shared_task()
def get_verification_code(whatsapp,connect_id, user_id):
    user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_2 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36"
    ]
    options = Options()
    options.add_argument(f"user-agent={random.choice(user_agents)}")
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--log-level=3")
    options.add_argument("--window-size=1280,720")  # Better screen size
    options.add_argument("--mute-audio")  # Audio processes ko disable kare
    options.add_argument("--disable-extensions")  # Extensions load na ho
    options.add_argument("--disable-background-timer-throttling")
    options.add_argument("--disable-backgrounding-occluded-windows")
    options.add_argument(f"--user-data-dir=/tmp/chrome_profile_{random.randint(1000,9999)}")
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
        numbers = ['9395982654','6000694134','984301450']
        simulate_typing(inputs[0], random.choice(numbers), typing_speed=0.2)
        simulate_typing(inputs[1], 'webshade124432', typing_speed=0.2)

        login_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'login_btn')))
        login_button.click()

        try:
            # Try to find and click "Close" button
            close_button = wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(., 'Close')]")))
            driver.execute_script("arguments[0].click();", close_button)
            print("Close button clicked.")
        except:
            print("Close button not found, moving to Start Task button.")

        try:
            button = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "startTaskBtn")))
            driver.execute_script("arguments[0].scrollIntoView();", button)
            button.click()
        except:
            status = update_error('Unable to get start',connect_id,pid)
            return status

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
        wait_time = 150  # Max wait time
        refresh_interval = 20  # Interval between refresh attempts
        start_time = time.time()
        last_refresh = time.time()
        while time.time() - start_time < wait_time:
            try:
                element = WebDriverWait(driver, 25).until(
                    EC.presence_of_element_located((By.XPATH, f"//div[@class='account_status']//div[@class='account' and contains(text(), '{whatsapp}')]"))
                )
                online_status = set_status_online(connect_id)
                print("Online status",online_status)
                if online_status:
                    return True
                status = update_error('Error while setting whatsapp online.',connect_id,pid)
                return status

            except:
                pass

            if time.time() - last_refresh >= refresh_interval:
                print('Clicking refresh')
                try:
                    refresh_button = WebDriverWait(driver, 25).until(
                        EC.element_to_be_clickable((By.CLASS_NAME, "updateList"))
                    )
                    refresh_button.click()
                    last_refresh = time.time()
                except:
                    traceback.print_exc()

            random_sleep(1, 2)
        status = update_error("Whatsapp didn't connect",connect_id,pid)
        return status

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
