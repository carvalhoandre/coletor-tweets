import os
import sys

import tweepy

from pymongo import MongoClient
from dotenv import load_dotenv
from flask import Flask, g
from flask_cors import CORS
from utils import error_handler
from config.settings import DevConfig, ProdConfig

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

def get_twitter_client():
    """Função para obter a conexão com a API do Twitter."""
    if "twitter_client" not in g:
        try:
            bearer_token = os.getenv("BEARER_TOKEN")
            if not bearer_token:
                raise ValueError("❌ BEARER_TOKEN não encontrado no .env")

            g.twitter_client = tweepy.Client(bearer_token)
            print("✅ Tweepy configurado com sucesso")

        except Exception as e:
            print(f"❌ Erro ao conectar ao Twitter API: {e}")
            sys.exit(1)

    return g.twitter_client

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
