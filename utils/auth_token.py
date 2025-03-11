import os
import sys
import random
import string

from flask import Flask
from flask_jwt_extended import create_access_token, JWTManager

def generate_token(identity: str) -> str:
    try:
        return create_access_token(identity=identity)
    except Exception as e:
        raise ValueError(f"Error generating token: {str(e)}")

def generate_confirmation_code(length=4):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def get_auth_token_app(app_identity: str) -> str:
    """Function to obtain application security token."""
    try:
        if not app_identity:
            raise ValueError("App ID not provided")

        token = generate_token(app_identity)

        return token
    except Exception as e:
        print(f"❌ Error getting token: {e}")
        sys.exit(1)

def handle_token():
    """Function to handle token."""
    app = Flask(__name__)

    jwt_secret_key = os.getenv('JWT_SECRET_KEY')

    if not jwt_secret_key:
        raise ValueError("❌ JWT_SECRET_KEY não encontrado no .env")
    app.config['JWT_SECRET_KEY'] = jwt_secret_key

    # Initializes the JWTManager
    JWTManager(app)

    # Creating a Token with Application Context
    with app.app_context():
        token = get_auth_token_app("my_app")
        if not token:
            print(f"❌ Erro ao iniciar aplicação")
            sys.exit(1)
        print(token)