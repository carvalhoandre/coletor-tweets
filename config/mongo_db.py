import os
from pymongo import MongoClient

environment = os.getenv('FLASK_ENV', 'dev')
MONGO_URI = os.getenv("DATABASE_MONGO_URI_PROD") if environment == 'prod' else os.getenv("DATABASE_MONGO_URI_DEV")

client = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=5000,
    tls=True,
    tlsAllowInvalidCertificates=False,
    tlsCAFile=None
)

try:
    client.admin.command('ping')
except Exception as e:
    raise Exception(f"Failed to connect to MongoDB: {e}")

def get_mongo_db():
    return client["twitter_db"]
