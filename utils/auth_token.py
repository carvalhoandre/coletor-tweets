import os
import sys
import random
import string
import bcrypt

from flask import Flask
from flask_jwt_extended import create_access_token, JWTManager


def generate_token(app_id):
    try:
        return create_access_token(identity=str(app_id))
    except Exception as e:
        raise ValueError(f"Error generating token: {str(e)}")

def generate_confirmation_code(length=4):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def get_auth_token_app(jwt_secret_key):
    """Function to obtain application security token."""
    try:
        if not jwt_secret_key:
            raise ValueError("❌ JWT_SECRET_KEY not found in .env")

        access_token = generate_token(jwt_secret_key)
        access_token_encode = bcrypt.hashpw(access_token.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        return access_token_encode
    except Exception as e:
        print(f"❌ Error getting token: {e}")
        sys.exit(1)

def handle_token():
    """Function to handle token."""
    app = Flask(__name__)

    # JWT Configuration
    jwt_secret_key = os.getenv('JWT_SECRET_KEY')
    if not jwt_secret_key:
        raise ValueError("❌ JWT_SECRET_KEY não encontrado no .env")
    app.config['JWT_SECRET_KEY'] = jwt_secret_key

    # Initializes the JWTManager
    JWTManager(app)

    # Creating a Token with Application Context
    with app.app_context():
        token = get_auth_token_app(jwt_secret_key)
        if not token:
            print(f"❌ Erro ao iniciar aplicação")
            sys.exit(1)
        print(token)