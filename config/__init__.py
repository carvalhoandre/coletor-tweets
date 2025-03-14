from dotenv import load_dotenv

from config.mongo_db import get_mongo_db
from config.settings import DevConfig, ProdConfig
import os
from dotenv import load_dotenv

from flask import Flask, g, request
from flask_cors import CORS

from config.mongo_db import get_mongo_db
from config.x_connect import get_twitter_client, close_twitter_client
from utils import error_handler
from config.settings import DevConfig, ProdConfig

load_dotenv()

def create_app(env='dev'):
    """Factory function to create Flask App instance."""
    app = Flask(__name__)

    env = env.lower()

    if env == "prod":
        app.config.from_object(ProdConfig)
    else:
        app.config.from_object(DevConfig)
        print("🛠️ Development Mode Enabled")

    cors_origins = os.getenv('BASE_URL', 'http://localhost:5173')

    CORS(
        app,
        resources={r"/*": {"origins": cors_origins}},
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
        methods=["GET", "POST", "OPTIONS"]
    )

    @app.after_request
    def apply_cors_headers(response):
        response.headers["Access-Control-Allow-Origin"] = request.headers.get("Origin", cors_origins)
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        return response

    @app.before_request
    def setup_services():
        try:
            g.mongo_db = get_mongo_db()
            g.twitter_client = get_twitter_client()
        except Exception as e:
            app.logger.error(f"Service initialization failed: {str(e)}")
            raise

    @app.teardown_appcontext
    def cleanup_services(exception=None):
        close_twitter_client(exception)

    try:
        from resources.tweets_resource import tweets_bp
        app.register_blueprint(tweets_bp)
    except ImportError as e:
        app.logger.error(f"❌ Blueprint registration failed: {str(e)}")

    app.register_error_handler(Exception, error_handler.handle_exception)

    return app
