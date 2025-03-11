from datetime import datetime
from time import sleep
from typing import List, Dict, Any, Optional

from pymongo.collection import Collection
from pymongo.errors import PyMongoError, DuplicateKeyError
from flask import current_app, g
import tweepy

from analytics.tweets_analytic import analytic_tweets

class TweetService:
    def __init__(self):
        self._tweets_collection: Optional[Collection] = None
        self._twitter_client: Optional[tweepy.Client] = None

    @property
    def metrics_collection(self) -> Collection:
        """
        Lazy-loaded MongoDB collection for tweet metrics
        """
        if 'mongo_db' not in g:
            current_app.logger.error("Database connection not initialized")
            raise RuntimeError("Database connection not initialized")
        return g.mongo_db["tweets_metrics"]

    @property
    def tweets_collection(self) -> Collection:
        """Lazy-loaded MongoDB tweets collection."""
        if self._tweets_collection is None:
            if 'mongo_db' not in g:
                current_app.logger.error("Database connection not initialized")
                raise RuntimeError("Database connection not initialized")
            self._tweets_collection = g.mongo_db["tweets"]
        return self._tweets_collection

    @property
    def twitter_client(self) -> tweepy.Client:
        """Lazy-loaded Twitter client."""
        if self._twitter_client is None:
            if not hasattr(g, 'twitter_client'):
                current_app.logger.error("Twitter client not initialized")
                raise RuntimeError("Twitter service unavailable")
            self._twitter_client = g.twitter_client
        return self._twitter_client

    def get_tweets(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Retrieve tweets.

        If force_refresh is False and cached tweets exist, returns cached tweets.
        Otherwise, fetches new tweets from Twitter API, processes, stores, and returns them.
        """
        try:
            if not force_refresh and self._has_cached_tweets():
                current_app.logger.debug("Returning cached tweets")
                return self._get_cached_tweets()

            current_app.logger.info("Fetching new tweets")
            raw_tweets = self._fetch_from_twitter()
            if not raw_tweets:
                raise ValueError("No tweets received from Twitter API")

            processed_tweets = self._process_tweets(raw_tweets)
            self._store_tweets(processed_tweets)
            return processed_tweets

        except (PyMongoError, tweepy.TweepyException) as e:
            current_app.logger.error(f"Tweet service failed: {str(e)}")
            raise RuntimeError("Tweet service operation failed") from e
        except Exception as e:
            current_app.logger.error(f"Unexpected error in tweet service: {str(e)}")
            raise

    def _has_cached_tweets(self) -> bool:
        """Check if there are any cached tweets in the database."""
        try:
            return self.tweets_collection.count_documents({}, limit=1) > 0
        except PyMongoError as e:
            current_app.logger.error(f"Cache check failed: {str(e)}")
            return False

    def _get_cached_tweets(self) -> List[Dict[str, Any]]:
        """Retrieve all stored tweets from the database with selected fields."""
        try:
            tweets_cursor = self.tweets_collection.find(
                {},
                {
                    "_id": 0,
                    "tweet_id": 1,
                    "text": 1,
                    "author": 1,
                    "created_at": 1,
                    "stored_at": 1,
                    "source": 1,
                    "processed": 1
                }
            )
            tweets = list(tweets_cursor)
            # Convert datetime objects to ISO format strings for output.
            for tweet in tweets:
                for field in ["created_at", "stored_at"]:
                    if field in tweet and isinstance(tweet[field], datetime):
                        tweet[field] = tweet[field].isoformat()
            return tweets
        except PyMongoError as e:
            current_app.logger.error(f"Cache retrieval failed: {str(e)}")
            return []

    def _fetch_from_twitter(self, max_retries: int = 3) -> List[Dict[str, Any]]:
        """
        Fetch raw tweets from Twitter API with retry logic for rate limits.

        Returns a list of tweet data dictionaries.
        """
        retries = 0
        while retries < max_retries:
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
                current_app.logger.warning(
                    f"Rate limited. Retrying in {retry_after}s (attempt {retries + 1}/{max_retries})"
                )
                sleep(retry_after)
                retries += 1
            except tweepy.TweepyException as e:
                current_app.logger.error(f"Twitter API error: {str(e)}")
                raise
        raise RuntimeError("Exceeded maximum retries due to rate limiting")

    @staticmethod
    def _process_tweets(raw_tweets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process raw tweets by adding metadata.

        Adds a 'stored_at' datetime, 'source', and a 'processed' flag.
        """
        current_time = datetime.utcnow()
        processed = []
        for tweet in raw_tweets:
            tweet_copy = tweet.copy()
            tweet_copy["tweet_id"] = tweet_copy.pop("id", None)
            tweet_copy["stored_at"] = current_time
            tweet_copy["source"] = "twitter_api"
            tweet_copy["processed"] = False
            processed.append(tweet_copy)
        return processed

    def _store_tweets(self, tweets: List[Dict[str, Any]]) -> None:
        """Store processed tweets in MongoDB."""
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
            current_app.logger.warning(f"Duplicate tweets detected and skipped: {str(e)}")
        except PyMongoError as e:
            current_app.logger.error(f"Storage failed: {str(e)}")
            raise

    def process_hourly_metrics(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Calculate the average hourly sentiment from tweets and save the results
        in the 'tweets_metrics' collection.

        Parameters:
        - force_refresh: If True, forces the retrieval of new tweets even if there is cached data.

        Returns:
        - A list of dictionaries with average hourly sentiment.
        """
        try:
            tweets = self.get_tweets(force_refresh=force_refresh)
            if not tweets:
                raise ValueError("No tweets available for metrics analysis")

            hourly_stats = analytic_tweets(tweets)

            if hourly_stats.empty:
                raise ValueError("No hourly stats received")

            hourly_stats_list = hourly_stats.to_dict("records")

            self.metrics_collection.insert_many(hourly_stats_list, ordered=False)
            current_app.logger.info("Hourly metrics saved successfully.")

            for doc in hourly_stats_list:
                if "_id" in doc:
                    doc["_id"] = str(doc["_id"])

            return hourly_stats_list
        except Exception as e:
            current_app.logger.error(f"Error saving hourly metrics: {str(e)}")
            raise
