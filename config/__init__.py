import os
import sys
import bcrypt

from pymongo import MongoClient
from dotenv import load_dotenv

from flask import Flask, g
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from utils import error_handler
from config.settings import DevConfig, ProdConfig
from utils.auth_token import generate_token

# 🔹 Carregar variáveis de ambiente
load_dotenv()

def get_mongo_db(env='dev'):
    """Função para obter a conexão com MongoDB."""
    is_production = env == 'prod'

    if "mongo_db" not in g:
        try:
            mongo_uri = os.getenv("DATABASE_MONGO_URI_PROD") if is_production else os.getenv("DATABASE_MONGO_URI_DEV")

            if not mongo_uri:
                raise ValueError(f"❌ DATABASE_MONGO_URI_{'PROD' if is_production else 'DEV'} não encontrado no .env")

            client = MongoClient(mongo_uri)
            g.mongo_db = client["twitter_db"]
            print(f"✅ Conectado ao MongoDB ({'PRODUÇÃO' if is_production else 'DESENVOLVIMENTO'})")

        except Exception as e:
            print(f"❌ Erro ao conectar ao MongoDB: {e}")
            sys.exit(1)

    return g.mongo_db

def get_auth_token_app(jwt_secret_key):
    """Função para obter token de segurança da aplicação."""
    try:
        if not jwt_secret_key:
            raise ValueError("❌ JWT_SECRET_KEY não encontrado no .env")

        access_token = generate_token(jwt_secret_key)
        access_token_encode = bcrypt.hashpw(access_token.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        return access_token_encode
    except Exception as e:
        print(f"❌ Erro ao obter token: {e}")
        sys.exit(1)

def create_app(env='dev'):
    """Factory function para criar a instância do Flask App."""
    app = Flask(__name__)

    # Configuração de CORS
    cors_url = os.getenv('BASE_URL', 'http://localhost:3000')
    CORS(app, resources={r"/*": {"origins": cors_url}},
         methods=["GET", "POST", "OPTIONS"],
         allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
         supports_credentials=True)

    # Configuração do ambiente Flask
    if env == "prod":
        app.config.from_object(ProdConfig)
    else:
        app.config.from_object(DevConfig)
        print("🛠️ Modo de Desenvolvimento ativado")

    # Configuração do JWT
    jwt_secret_key = os.getenv('JWT_SECRET_KEY')
    if not jwt_secret_key:
        raise ValueError("❌ JWT_SECRET_KEY não encontrado no .env")
    app.config['JWT_SECRET_KEY'] = jwt_secret_key  # Define a chave secreta

    # Inicializa o JWTManager
    JWTManager(app)

    # Criação do Token com Application Context
    with app.app_context():
        token = get_auth_token_app(jwt_secret_key)
        if not token:
            print(f"❌ Erro ao iniciar aplicação")
            sys.exit(1)
        print(token)

    # Registrar tratamento de erros
    app.register_error_handler(Exception, error_handler.handle_exception)

    @app.teardown_appcontext
    def close_connection(exception):
        """Fecha a conexão com o MongoDB e remove o cliente Tweepy no fim da requisição."""
        mongo_db = g.pop("mongo_db", None)
        if mongo_db:
            mongo_db.client.close()
            print("🔻 Conexão com MongoDB encerrada.")

        twitter_client = g.pop("twitter_client", None)
        if twitter_client:
            print("🔻 Cliente Tweepy removido.")

    return app
