import os

from dotenv import load_dotenv

from flask import Flask, g
from flask_cors import CORS

from utils import error_handler
from config.settings import DevConfig, ProdConfig
from utils.auth_token import handle_token

load_dotenv()

def create_app(env='dev'):
    """Factory function to create Flask App instance."""
    app = Flask(__name__)

    # CORS Configuration
    cors_url = os.getenv('BASE_URL', 'http://localhost:3000')
    CORS(app, resources={r"/*": {"origins": cors_url}},
         methods=["GET", "POST", "OPTIONS"],
         allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
         supports_credentials=True)

    # Flask environment setup
    if env == "prod":
        app.config.from_object(ProdConfig)
    else:
        app.config.from_object(DevConfig)
        print("🛠️ Development Mode Enabled")

    handle_token()

    app.register_error_handler(Exception, error_handler.handle_exception)

    @app.teardown_appcontext
    def close_connection(exception):
        """Closes the connection to MongoDB and removes the Tweepy client at the end of the request."""
        mongo_db = g.pop("mongo_db", None)
        if mongo_db:
            mongo_db.client.close()
            if env == "dev":
                print("MongoDB connection closed")

        twitter_client = g.pop("twitter_client", None)
        if twitter_client and env == "dev":
            print("Tweepy client removed")

    return app
