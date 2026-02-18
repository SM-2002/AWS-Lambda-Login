import re

def validate_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) 

def validate_phone(phone):
    pattern = r'^\+91[6-9]\d{9}$'
    return re.match(pattern, phone)

def is_strong_password(password):
    pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z\d]).{8,}$'
    return re.match(pattern, password)