import random
from datetime import datetime
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
