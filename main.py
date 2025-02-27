import os
import tweepy
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Retrieve credentials
api_key = os.getenv('API_KEY')
api_secret = os.getenv('API_SECRET')
bearer_token = os.getenv('BEARER_TOKEN')
mongo_client = os.getenv('MONGO_CLIENT')

# Verify if environment variables are loaded
if not all([api_key, api_secret, bearer_token, mongo_client]):
    raise ValueError("One or more environment variables are missing!")

# Connect to MongoDB Atlas
client = MongoClient(mongo_client)
db = client["twitter_db"]

class XListener(tweepy.StreamingClient):
    def on_tweet(self, tweet):
        tweet_data = {
            "text": tweet.text,
            "id": tweet.id,
            "created_at": tweet.created_at if hasattr(tweet, "created_at") else None
        }
        db.raw_tweets.insert_one(tweet_data)
        print(f"Tweet salvo: {tweet.text[:50]}...")

stream = XListener(bearer_token)

stream.add_rules(tweepy.StreamRule("filme"))

print("Iniciando coleta de tweets...")
stream.filter()
