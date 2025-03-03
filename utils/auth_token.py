from flask_jwt_extended import create_access_token
import random
import string

def generate_token(app_id):
    try:
        return create_access_token(identity=str(app_id))
    except Exception as e:
        raise ValueError(f"Error generating token: {str(e)}")

def generate_confirmation_code(length=4):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
