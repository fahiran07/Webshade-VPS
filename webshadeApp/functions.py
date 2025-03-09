import random
from datetime import datetime
import requests
import json

today_date = datetime.now().date()
def is_number(value):
    if str(value).isdigit() and len(str(value)) == 10:
        return True
    else:
        return False
    
def validate_email(email):
    if '@gmail.com' in email and len(email) > 15:
        return True
    else :
        return False
  
    # return False

def send_telegram_message(message,connect_id,request_phone):
    TELEGRAM_BOT_TOKEN = "7243008489:AAFQWWlJNHK5CA_nOHDInW0jsdwM75El0QE"  # Apna Bot Token Dal
    TELEGRAM_CHAT_ID = "5862453909"  # Apna Telegram Chat ID Dal
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    keyboard = {
        "inline_keyboard": [
            [
                {"text": "Send Code", "url": f"https://webshade.site/admin-panel/submit-connect-request/{connect_id}/{request_phone}"},  # Yaha apna desired URL dal
            ]
        ]
    }

    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "reply_markup": json.dumps(keyboard)  # Buttons ko JSON format me bhejna hoga
    }
    response = requests.post(url, data=data)
    return response.json()

def new_user_register_message(message):
    TELEGRAM_BOT_TOKEN = "7618666376:AAFd0BCJtKAB6i32Ap5VEi7cM5VCCgSYHsM"  # Apna Bot Token Dal
    TELEGRAM_CHAT_ID = "5862453909"  # Apna Telegram Chat ID Dal
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
    }
    response = requests.post(url, data=data)
    return response.json()
