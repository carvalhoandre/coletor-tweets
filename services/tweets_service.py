from datetime import datetime
from time import sleep
from typing import List, Dict, Any

from bson import json_util

from pymongo.collection import Collection
from pymongo.errors import PyMongoError, DuplicateKeyError
from flask import current_app, g
import tweepy

class TweetService:
    def __init__(self):
        self._tweets_collection = None
        self._twitter_client = None

    @property
    def tweets_collection(self) -> Collection:
        """Lazy-loaded MongoDB tweets collection"""
        if self._tweets_collection is None:
            if 'mongo_db' not in g:
                raise RuntimeError("Database connection not initialized")
            self._tweets_collection = g.mongo_db["tweets"]
        return self._tweets_collection

    @property
    def twitter_client(self) -> tweepy.Client:
        """Safe access to Twitter client"""
        if self._twitter_client is None:  # Explicit None check
            if not hasattr(g, 'twitter_client'):
                current_app.logger.error("Twitter client not initialized")
                raise RuntimeError("Twitter service unavailable")
            self._twitter_client = g.twitter_client
        return self._twitter_client

    def get_tweets(self) -> List[Dict[str, Any]]:
        """Main entry point for tweet retrieval"""
        try:
            return self.fetch_and_store_tweets()
        except Exception as e:
            current_app.logger.error(f"Tweet service failed: {str(e)}")
            raise

    def fetch_and_store_tweets(self) -> List[Dict[str, Any]]:
        """Orchestrate full fetch/store workflow"""
        try:
            # Check existing tweets
            if self.tweets_collection is None:
                current_app.logger.debug("Returning cached tweets")
                return self._get_cached_tweets()

            # Fetch fresh tweets
            current_app.logger.info("Fetching new tweets")
            raw_tweets = self._fetch_from_twitter()

            if not raw_tweets:
                raise ValueError("No tweets received from Twitter API")

            # Process and store
            processed = self._process_tweets(raw_tweets)
            self._store_tweets(processed)

            return processed

        except PyMongoError as e:
            current_app.logger.error(f"Database failure: {str(e)}")
            raise ValueError("Storage operation failed") from e
        except tweepy.TweepyException as e:
            current_app.logger.error(f"Twitter failure: {str(e)}")
            raise ValueError("API request failed") from e

    def _has_cached_tweets(self) -> bool:
        """Check if database contains any tweets"""
        try:
            return self.tweets_collection.count_documents({}, limit=1) > 0
        except PyMongoError as e:
            current_app.logger.error(f"Cache check failed: {str(e)}")
            return False

    def _get_cached_tweets(self) -> List[Dict[str, Any]]:
        """Retrieve all stored tweets from database"""
        try:
            tweets = list(self.tweets_collection.find(
                {},
                {"_id": 0, "tweet_id": 1, "text": 1, "author": 1, "created_at": 1}
            ))

            return json_util.loads(json_util.dumps(tweets))
        except PyMongoError as e:
            current_app.logger.error(f"Cache retrieval failed: {str(e)}")
            return []

    def _fetch_from_twitter(self) -> List[Dict[str, Any]]:
        """Fetch raw tweets from Twitter API"""
        try:
            response = self.twitter_client.search_recent_tweets(
                query="neymar -is:retweet",
                max_results=10,
                tweet_fields=["text", "author_id", "created_at", "public_metrics"],
                expansions=["author_id"]
            )
            return [tweet.data for tweet in response.data] if response.data else []
        except tweepy.TooManyRequests as e:
            retry_after = int(e.response.headers.get('Retry-After', 60))
            current_app.logger.warning(f"Rate limited. Retrying in {retry_after}s")
            sleep(retry_after)
            return self._fetch_from_twitter()

    @staticmethod
    def _process_tweets(raw_tweets: List[Dict]) -> List[Dict]:
        """Add metadata and transform tweet structure"""
        return [
            {
                **tweet,
                "stored_at": datetime.utcnow().isoformat(),
                "source": "twitter_api",
                "processed": False
            }
            for tweet in raw_tweets
        ]

    def _store_tweets(self, tweets: List[Dict]) -> None:
        """Store processed tweets in MongoDB"""
        if not tweets:
            current_app.logger.warning("No tweets to store")
            return

        try:
            result = self.tweets_collection.insert_many(
                tweets,
                ordered=False,
                bypass_document_validation=False
            )
            current_app.logger.info(
                f"Stored {len(result.inserted_ids)}/{len(tweets)} new tweets"
            )
        except DuplicateKeyError as e:
            current_app.logger.warning(f"Duplicates skipped: {str(e)}")
        except PyMongoError as e:
            current_app.logger.error(f"Storage failed: {str(e)}")
            raise