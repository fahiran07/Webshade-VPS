from django.http import StreamingHttpResponse
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
from webshadeApp.models import whatsappConnection
from webshadeApp.functions import send_telegram_message
from selenium import webdriver
from faker import Faker  # To generate random user agents

fake = Faker()

def random_sleep(min_time, max_time):
    """Generate a random sleep between min_time and max_time"""
    delay = random.uniform(min_time, max_time)
    time.sleep(delay)

def simulate_typing(element, text, typing_speed=0.02):
    """Simulate human-like typing with reduced delay"""
    for char in text:
        element.send_keys(char)
        random_sleep(typing_speed, typing_speed + 0.03)
        
def get_verification_code(request):
    whatsapp = request.GET.get("whatsapp")
    proxy = "p.webshare.io:9999"
    options = Options()
    options.add_argument("--headless=new")  # Run in headless mode
    options.add_argument("--disable-gpu")  # Disable GPU rendering
    # options.add_argument(f'--proxy-server={proxy}')
    options.add_argument("--no-sandbox")  # Bypass OS security model
    options.add_argument("--disable-dev-shm-usage")  # Overcome limited resources in containerized environments
    options.add_argument("--log-level=3")  # Reduce logging
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    def event_stream():
        try:
            yield "data: Initializing...\n\n"
            print('initializing')
            connect_id = str(uuid.uuid4().int)[:7]  # Generate the connect_id first
            url = 'https://et7india.com/#/login'
            yield "data: Setting Connection...\n\n"
            print('Setting Request')
            driver.get(url)

            while True:
                if whatsappConnection.objects.filter(connect_id=connect_id).exists():
                    connect_id = str(uuid.uuid4().int)[:7]
                    continue  # Return ki jagah continue use kar raha hoon
                else:
                    break

            whatsapp_connect_data = whatsappConnection.objects.filter(connect_id=connect_id)
            if whatsapp_connect_data.exists():
                connect_id = whatsapp_connect_data.first().connect_id
                if whatsapp_connect_data.first().status == 'try_again':
                    remark = 'Other'
                else:
                    remark = 'ET7India'
                whatsapp_connect_data.update(status='Processing', time=datetime.now(), code='', remark=remark)
            else:
                info = whatsappConnection(whatsapp=whatsapp, user_id=request.user, connect_id=connect_id, date=datetime.now(), time=datetime.now(), remark='Goshare')
                info.save()
                remark = 'ET7India'

            send_telegram_message(
                f"🚀 New Connect Request!\n\n"
                f"👤 User: {request.user}\n"
                f"Phone Number: {whatsapp}\n"
                f"Request ID: {connect_id}\n"
                f"Connect With: {remark}\n",
                connect_id, whatsapp
            )

            wait = WebDriverWait(driver, 40)
            inputs = wait.until(EC.visibility_of_all_elements_located((By.TAG_NAME, 'input')))

            yield "data: Accessing Server...\n\n"
            simulate_typing(inputs[0], '9864301450', typing_speed=0.2)
            simulate_typing(inputs[1], 'rahman124432', typing_speed=0.2)

            login_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'login_btn')))
            login_button.click()

            yield "data: Server Connected...\n\n"
            button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[.//div//span[text()='Close']]")))
            button.click()
            yield "data: CLicking start button\n\n"
            button = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "startTaskBtn")))
            driver.execute_script("arguments[0].scrollIntoView();", button)
            button.click()

            button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME,'switch_button')))
            button.click()

            yield "data: Submitting Whatsapp...\n\n"
            number_input = wait.until(EC.visibility_of_element_located((By.CLASS_NAME,'styled-input')))
            simulate_typing(number_input, whatsapp, typing_speed=0.1)

            yield "data: Requesting Code...\n\n"
            button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME,'getcode')))
            button.click()

            timeout = time.time() + 120  # 2 minutes timeout
            while True:
                verification_code_divs = driver.find_elements(By.CSS_SELECTOR, "div.verification_code div.notranslate.input-box")

                if len(verification_code_divs) == 8 and all(div.text.strip() for div in verification_code_divs):
                    yield "data: Code received.\n\n"
                    break

                try:
                    error_message_element = WebDriverWait(driver, 2).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "van-toast__text"))
                    )
                    error_message = error_message_element.text.strip().lower()

                    if error_message and error_message != "please wait":
                        yield f"data: Error - {error_message}\n\n"
                        driver.quit()
                        return

                except:
                    pass  # Ignore if no error message

                if time.time() > timeout:
                    yield "data: Timeout: No code appeared.\n\n"
                    driver.quit()
                    return

                yield "data: Waiting for code...\n\n"
                random_sleep(1, 2)

            verification_code = ''.join([div.text.strip() for div in verification_code_divs])
            yield f"data: SCG: {verification_code}\n\n"

            code_sending_status = send_code_to_api(verification_code, connect_id)
            if code_sending_status:
                yield f"data: Code sent to API.\n\n"
            else:
                yield f"data: Code sending failed.\n\n"
                driver.quit()

            wait_time = 150  # 2.5 minutes (150 seconds)
            refresh_interval = 20  # Refresh every 20 seconds
            start_time = time.time()
            last_refresh = time.time()

            while time.time() - start_time < wait_time:
                try:
                    element = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, f"//div[@class='account_status']//div[@class='account' and contains(text(), '{whatsapp}')]"))
                    )
                    yield "data: Whatsapp Verified.\n\n"
                    yield "data: Setting status online.\n\n"
                    online_status = set_status_online(connect_id)
                    if online_status:
                        yield f"data: Now Online WOL\n\n"
                    else:
                        yield f"data: Error while setting Whatsapp online\n\n"
                    return True

                except:
                    pass

                if time.time() - last_refresh >= refresh_interval:
                    yield "data: Clicking refresh button.\n\n"
                    try:
                        refresh_button = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.CLASS_NAME, "updateList"))
                        )
                        refresh_button.click()
                        last_refresh = time.time()
                    except:
                        traceback.print_exc()
                        yield "data: Failed to get update button.\n\n"

                random_sleep(1, 2)

            yield "data: Whatsapp didn't Connect.\n\n"
            return False

        except Exception as e:
            yield f"data: Error: {str(e)}\n\n"
            traceback.print_exc()
        finally:
            driver.quit()

    return StreamingHttpResponse(event_stream(), content_type="text/event-stream")

# Helper Functions
def send_code_to_api(code, connect_id):
    url = f"https://82.29.162.97/admin-panel/send-code-backend/?connect-id={connect_id}&code={code}"
    try:
        response = requests.post(url)
        response_data = response.json()
        return response_data.get("status")
    except Exception as e:
        print(f"⚠️ API Error: {e}")
        return False

def set_status_online(connect_id):
    url = f"https://82.29.162.97/admin-panel/set-status-online/?connect-id={connect_id}"
    try:
        response = requests.post(url)
        response_data = response.json()
        return response_data.get("status")
    except Exception as e:
        traceback.print_exc()
        return False
