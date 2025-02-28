import os
import tweepy
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Retrieve credentials
bearer_token = os.getenv('BEARER_TOKEN')
mongo_uri  = os.getenv('MONGO_CLIENT')

# Verify if environment variables are loaded
if not all([bearer_token, mongo_uri]):
    raise ValueError("One or more environment variables are missing!")

# Connect to MongoDB Atlas
client = MongoClient(mongo_uri)
db = client["twitter_db"]
collection = db["tweets"]

client = tweepy.Client(bearer_token)

query = "filme -is:retweet"
tweets = client.search_recent_tweets(query=query, max_results=10)

if not tweets:
    print("❌ Nenhum tweet encontrado.")
    raise ValueError("No tweets found!")

for tweet in tweets.data:
    collection.insert_one(tweet)

print("✅ Tweets salvos com sucesso!")

client.close()
