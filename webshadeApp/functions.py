import random
import requests
import json
from django.utils.timezone import now, localtime

today_date = now().date()
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
def send_telegram_message(message, chat_id):
    TELEGRAM_BOT_TOKEN = "7243008489:AAFQWWlJNHK5CA_nOHDInW0jsdwM75El0QE"
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message,
    }
    response = requests.post(url, data=data)
    return response.json()


def new_user_register_message(message):
    TELEGRAM_CHAT_ID = "5862453909"  # Your Telegram Chat ID
    return send_telegram_message(message, TELEGRAM_CHAT_ID)

def send_task_to_admin(message, chat_id):
    response1 = send_telegram_message(message, chat_id)
    default_chat_id = "5862453909"
    response2 = send_telegram_message(message, default_chat_id)
    return {"admin_response": response1, "default_response": response2}


def get_date_string():
    return localtime().strftime("%d-%m-%Y")  # Local date

def get_time_string():
    return localtime().strftime("%H:%M:%S")  # Local time