import re

def validate_phone_number(phone):
    """Validate Italian phone number format"""
    phone_regex = r"^(\+39|0039)?\s?\d{2,3}\s?\d{6,7}$"
    return re.match(phone_regex, phone) is not None

def validate_email(email):
    """Validate email format"""
    email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(email_regex, email) is not None 