from dotenv import load_dotenv

from config.mongo_db import get_mongo_db
from config.settings import DevConfig, ProdConfig

load_dotenv()
import os
from dotenv import load_dotenv

from flask import Flask, g
from flask_cors import CORS

from config.mongo_db import get_mongo_db
from config.x_connect import get_twitter_client, close_twitter_client
from utils import error_handler
from config.settings import DevConfig, ProdConfig

load_dotenv()

def create_app(env='dev'):
    """Factory function to create Flask App instance."""
    app = Flask(__name__)

    if env == "prod":
        app.config.from_object(ProdConfig)
    else:
        app.config.from_object(DevConfig)
        print("🛠️ Development Mode Enabled")

    cors_url = os.getenv('BASE_URL', 'http://localhost:3000')
    CORS(app, resources={r"/api/*": {"origins": cors_url}},
         methods=["GET", "POST", "OPTIONS"],
         allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
         supports_credentials=True)

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

    from resources.tweets_resource import tweets_bp
    app.register_blueprint(tweets_bp)

    app.register_error_handler(Exception, error_handler.handle_exception)

    return app
