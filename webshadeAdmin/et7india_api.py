from django.http import StreamingHttpResponse
import time
import traceback
from selenium import webdriver
import requests
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

def get_verification_code(request):
    whatsapp = request.GET.get("whatsapp")
    connect_id = request.GET.get("connect-id")
    options = Options()
    options.add_argument("--headless=new")  # Run in headless mode
    options.add_argument("--disable-gpu")  # Disable GPU rendering
    options.add_argument("--no-sandbox")  # Bypass OS security model
    options.add_argument("--disable-dev-shm-usage")  # Overcome limited resources in containerized environments
    options.add_argument("--log-level=3")  # Reduce logging
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    def event_stream():
        try:
            yield "data: Initializing browser...\n\n"

            # Define URL
            url = 'https://et7india.com/#/login'
            yield "data: Opening website...\n\n"
            driver.get(url)

            wait = WebDriverWait(driver, 30)  # Max 25 sec wait
            inputs = wait.until(EC.visibility_of_all_elements_located((By.TAG_NAME, 'input')))

            yield "data: Entering login details...\n\n"
            inputs[0].send_keys('9864301450')
            inputs[1].send_keys('rahman124432')

            yield "data: Clicking login...\n\n"
            login_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'login_btn')))
            login_button.click()

            yield "data: Closing popup...\n\n"
            button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[.//div//span[text()='Close']]")))
            button.click()

            yield "data: Starting task...\n\n"
            button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "startTaskBtn")))
            driver.execute_script("arguments[0].scrollIntoView();", button)
            button.click()

            yield "data: Switching task...\n\n"
            button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME,'switch_button')))
            button.click()

            yield "data: Entering phone number...\n\n"
            number_input = wait.until(EC.visibility_of_element_located((By.CLASS_NAME,'styled-input')))
            number_input.send_keys(whatsapp)  # Provided WhatsApp number

            yield "data: Requesting verification code...\n\n"
            button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME,'getcode')))
            button.click()

            timeout = time.time() + 120  # 2 minutes timeout

            while True:
                # ✅ Check if Verification Code Boxes Appear
                verification_code_divs = driver.find_elements(By.CSS_SELECTOR, "div.verification_code div.notranslate.input-box")

                if len(verification_code_divs) == 8 and all(div.text.strip() for div in verification_code_divs):
                    yield "data: Verification code received successfully.\n\n"
                    break  # If all 8 boxes have text, exit loop
                
                # ✅ Check if Error Message Appears (But Ignore "please wait")
                try:
                    error_message_element = WebDriverWait(driver, 2).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "van-toast__text"))
                    )
                    error_message = error_message_element.text.strip().lower()  # Convert to lowercase

                    if error_message and error_message != "please wait":
                        yield f"data: Error - {error_message}\n\n"
                        driver.quit()
                        return

                except:
                    pass  # Agar error message nahi dikha, toh ignore karke loop continue kar
                
                # ✅ Timeout Check
                if time.time() > timeout:
                    yield "data: Timeout: Not all 8 verification codes appeared.\n\n"
                    driver.quit()
                    return

                yield "data: Waiting for verification code...\n\n"
                time.sleep(1)

            verification_code = ''.join([div.text.strip() for div in verification_code_divs])
            yield f"data: Verification Code: {verification_code}\n\n"

            verification_status = send_code_to_api(verification_code, connect_id)
            yield f"data: Verification Status: {verification_status}\n\n"
            yield f"data: Started Verification\n\n"
            wait_time = 150  # 2.5 minutes (150 seconds)
            refresh_interval = 20  # Har 20 second baad button click hoga
            start_time = time.time()
            last_refresh = time.time()
            while time.time() - start_time < wait_time:
                try:
                    # Phone number milne ka wait kar
                    element = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH,f"//div[@class='account_status']//div[@class='account' and contains(text(), '{whatsapp}')]"))
                    )
                    yield "data: Whatsapp Verfied.\n\n"
                    yield "data: Setting status online.\n\n"
                    online_status = set_status_online(connect_id)
                    if online_status:
                        yield f"data: Whatsapp is now online \n\n"
                    else:
                        yield f"data: Error while whatsapp online \n\n"
                    return True  # Mil gaya to function yahi return ho jayega
                except:
                    pass  # Agar nahi mila to ignore kar aur niche ka code chalayega
                
                # Har 20 second ke baad button dabana hai
                if time.time() - last_refresh >= refresh_interval:
                    yield "data: Clicking refresh button.\n\n"
                    try:
                        refresh_button = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.CLASS_NAME, "updateList"))
                        )
                        refresh_button.click()
                        last_refresh = time.time()  # Refresh ka time update kar
                    except:
                        traceback.print_exc()
                        yield "data: Failed to get update button.\n\n"

                time.sleep(1)  # 1 second ka delay taaki CPU overload na ho

            yield "data: Whatsapp didn't Connect.\n\n"
            return False  # Agar 2.5 minutes tak nahi mila to False return karega
            online_status = set_status_online('000004')
            if online_status:
                yield f"data: Now Online \n\n"
            else:
                yield f"data: Error while whatsapp online \n\n"
        except Exception as e:
            yield f"data: Error: {str(e)}\n\n"
            traceback.print_exc()
        finally:
            driver.quit()

    return StreamingHttpResponse(event_stream(), content_type="text/event-stream")

def send_code_to_api(code,connect_id):
    url = f"http://127.0.0.1:8000/admin-panel/send-code-backend/?connect-id={connect_id}&code={code}"  # ✅ API URL for verification
    try:
        response = requests.post(url)  # ✅ Send Code
        response_data = response.json()
        return response_data.get("status")

    except Exception as e:
        print(f"⚠️ API Error: {e}")
        return False

def set_status_online(connect_id):
    url = f"http://127.0.0.1:8000/admin-panel/set-status-online/?connect-id={connect_id}"  # ✅ API URL for verification
    try:
        response = requests.post(url)  # ✅ Send Code
        response_data = response.json()
        return response_data.get("status")

    except Exception as e:
        traceback.print_exc()
        return False
