import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

uri = os.getenv('MONGO_CLIENT')

if not uri:
    print("No connection uri provided")
    exit(1)

client = MongoClient(uri)

db = client["twitter_db"]
collection = db[("test_peoples")]

data = [
    {"nome": "Alice", "idade": 25, "cidade": "São Paulo"},
    {"nome": "Bob", "idade": 30, "cidade": "Rio de Janeiro"},
    {"nome": "Carlos", "idade": 35, "cidade": "Belo Horizonte"},
]

collection.insert_many(data)

# 🔹 Consultar e imprimir os dados
print("📌 Dados no MongoDB:")
for doc in collection.find():
    print(doc)

# 🔹 Fechar conexão
client.close()
