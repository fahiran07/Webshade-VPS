import random
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
def get_date_string():
    return localtime().strftime("%d-%m-%Y")  # Local date

def get_time_string():
    return localtime().strftime("%H:%M:%S")  # Local time