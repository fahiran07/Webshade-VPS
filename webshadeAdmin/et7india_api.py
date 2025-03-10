from django.http import JsonResponse
import random
import time
import uuid
import requests
import traceback
from datetime import datetime
from playwright.sync_api import sync_playwright
from webshadeApp.models import whatsappConnection
from webshadeApp.functions import send_telegram_message

def random_sleep(min_time, max_time):
    time.sleep(random.uniform(min_time, max_time))

def get_verification_code(request):
    whatsapp = request.GET.get("whatsapp")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        try:
            connect_id = str(uuid.uuid4().int)[:7]
            url = 'https://et7india.com/#/login'
            page.goto(url, timeout=60000)

            while whatsappConnection.objects.filter(connect_id=connect_id).exists():
                connect_id = str(uuid.uuid4().int)[:7]

            whatsapp_connect_data = whatsappConnection.objects.filter(connect_id=connect_id)
            if whatsapp_connect_data.exists():
                connect_id = whatsapp_connect_data.first().connect_id
                remark = 'ET7India' if whatsapp_connect_data.first().status != 'try_again' else 'Other'
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

            # Login
            page.fill("input[type='text']", "9864301450")
            page.fill("input[type='password']", "rahman124432")
            page.click(".login_btn")

            # Close any popups
            page.wait_for_selector("//button[.//div//span[text()='Close']]", timeout=30000).click()

            # Start task
            page.wait_for_selector(".startTaskBtn", timeout=30000).click()
            page.wait_for_selector(".switch_button", timeout=30000).click()

            # Enter WhatsApp number
            page.fill(".styled-input", whatsapp)

            # Request verification code
            page.wait_for_selector(".getcode", timeout=30000).click()

            timeout = time.time() + 120  # 2 minutes timeout
            verification_code = None

            while time.time() < timeout:
                verification_code_divs = page.query_selector_all("div.verification_code div.notranslate.input-box")
                if len(verification_code_divs) == 8 and all(div.text_content().strip() for div in verification_code_divs):
                    verification_code = ''.join([div.text_content().strip() for div in verification_code_divs])
                    break
                random_sleep(1, 2)

            if not verification_code:
                return JsonResponse({"status": "error", "message": "No verification code received"}, status=400)
            print('Code is : ', verification_code)
            # Send code to API
            code_sending_status = send_code_to_api(verification_code, connect_id)
            if not code_sending_status:
                return JsonResponse({"status": "error", "message": "Failed to send code to API"}, status=400)

            # **Check if WhatsApp is verified**
            timeout = time.time() + 150  # 2.5 minutes timeout
            while time.time() < timeout:
                try:
                    element = page.wait_for_selector(f"//div[@class='account_status']//div[@class='account' and contains(text(), '{whatsapp}')]", timeout=5000)
                    if element:
                        # WhatsApp verified, set online status
                        online_status = set_status_online(connect_id)
                        if online_status:
                            return JsonResponse({"status": "success", "verification_code": verification_code, "message": "WhatsApp Verified & Online"})
                        else:
                            return JsonResponse({"status": "error", "message": "WhatsApp Verified but failed to set online"}, status=400)
                except:
                    pass

                # Refresh the page every 20 seconds
                if (time.time() % 20) == 0:
                    try:
                        page.wait_for_selector(".updateList", timeout=5000).click()
                    except:
                        pass

                random_sleep(1, 2)

            return JsonResponse({"status": "error", "message": "WhatsApp verification failed"}, status=400)

        except Exception as e:
            traceback.print_exc()
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

        finally:
            browser.close()

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
