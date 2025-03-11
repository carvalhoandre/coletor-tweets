import os

from dotenv import load_dotenv

from flask import Flask, g, current_app
from flask_cors import CORS

from config.mongo_db import get_mongo_db
from utils import error_handler
from config.settings import DevConfig, ProdConfig

load_dotenv()

def create_app(env='dev'):
    """Factory function to create Flask App instance."""
    app = Flask(__name__)

    from config.x_connect import get_twitter_client, close_twitter_client

    @app.before_request
    def setup_services():
        """Initialize required services before each request"""
        try:
            g.mongo_db = get_mongo_db()
            g.twitter_client = get_twitter_client()
        except Exception as e:
            app.logger.error(f"Service initialization failed: {str(e)}")
            raise

    @app.teardown_appcontext
    def cleanup_services(exception=None):
        """Cleanup resources after request"""
        close_mongo_connection(exception)
        close_twitter_client(exception)

    @app.before_request
    def setup_mongo():
        try:
            g.mongo_db = get_mongo_db()
        except Exception as e:
            app.logger.error(f"Pre-request DB setup failed: {str(e)}")
            raise

    from config.x_connect import close_twitter_client
    app.teardown_appcontext(close_twitter_client)

    # CORS Configuration
    cors_url = os.getenv('BASE_URL', 'http://localhost:3000')
    CORS(app, resources={r"/api/*": {"origins": cors_url}},
         methods=["GET", "POST", "OPTIONS"],
         allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
         supports_credentials=True)

    # Flask environment setup
    if env == "prod":
        app.config.from_object(ProdConfig)
    else:
        app.config.from_object(DevConfig)
        print("🛠️ Development Mode Enabled")

    from resources.tweets_resource import tweets_bp
    app.register_blueprint(tweets_bp)

    app.register_error_handler(Exception, error_handler.handle_exception)

    @app.teardown_appcontext
    def close_mongo_connection(exception=None):
        db = g.pop('mongo_db', None)
        if db is not None:
            db.client.close()
            current_app.logger.debug("🚪 MongoDB connection closed")

    return app
