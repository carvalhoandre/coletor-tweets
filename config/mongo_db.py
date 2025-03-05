import os
import sys

from pymongo import MongoClient
from flask import g

def get_mongo_db():
    """Function to get the connection to MongoDB."""
    is_production =  os.getenv("DATABASE_MONGO_URI_PROD") == 'prod'

    if "mongo_db" not in g:
        try:
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
