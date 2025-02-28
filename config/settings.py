import os

class DevConfig:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_MONGO_URI_DEV')
    BASE_URL= os.getenv('BASE_URL_DEV')

class ProdConfig:
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_MONGO_URI_PROD')
    BASE_URL= os.getenv('BASE_URL_PROD')
