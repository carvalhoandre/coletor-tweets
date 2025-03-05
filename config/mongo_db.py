import os
import sys

from flask import g, current_app

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure


def get_mongo_db():
    """Initialize MongoDB connection with proper error handling"""
    if 'mongo_db' not in g:
        is_production = os.getenv("DATABASE_MONGO_URI_PROD") == 'prod'
        mongo_uri = os.getenv("DATABASE_MONGO_URI_PROD") if is_production else os.getenv("DATABASE_MONGO_URI_DEV")

        try:
            client = MongoClient(
                mongo_uri,
                serverSelectionTimeoutMS=5000
            )

            # Verify connection
            client.admin.command('ping')
            g.mongo_db = client["twitter_db"]
            current_app.logger.info("✅ MongoDB connection established")
        except ConnectionFailure as e:
            current_app.logger.error(f"❌ MongoDB connection failed: {str(e)}")
            raise
    return g.mongo_db

def get_mongo_db_singleton():
    """Function to get the connection to MongoDB."""
    is_production =  os.getenv("DATABASE_MONGO_URI_PROD") == 'prod'

    if "mongo_db" not in g:
        try:
            with current_app.app_context():
                mongo_uri = os.getenv("DATABASE_MONGO_URI_PROD") if is_production else os.getenv("DATABASE_MONGO_URI_DEV")

                if not mongo_uri:
                    raise ValueError(f"❌ DATABASE_MONGO_URI_{'PROD' if is_production else 'DEV'} not found in .env")

                client = MongoClient(mongo_uri)
                g.mongo_db = client["twitter_db"]

                if not is_production:
                    print(f"✅ Connected to MongoDB ({'PRODUÇÃO' if is_production else 'DESENVOLVIMENTO'})")

        except Exception as e:
            print(f"❌ Error connecting to MongoDB: {e}")
            sys.exit(1)

    return g.mongo_db
