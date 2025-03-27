from datetime import datetime
from time import sleep
from typing import List, Dict, Any, Optional

from pymongo.collection import Collection
from pymongo.errors import PyMongoError, DuplicateKeyError
from flask import g
import tweepy

from analytics.tweets_analytic import analytic_tweets, calculate_hype_score
from preprocess.tweets_preprocess import process_tweet

from utils.logger import handle_logger

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
            handle_logger(message="Database connection not initialized", type_logger="error")
            raise RuntimeError("Database connection not initialized")
        return g.mongo_db["tweets_metrics"]

    @property
    def tweets_collection(self) -> Collection:
        """Lazy-loaded MongoDB tweets collection."""
        if self._tweets_collection is None:
            if 'mongo_db' not in g:
                handle_logger(message="Database connection not initialized", type_logger="error")
                raise RuntimeError("Database connection not initialized")
            self._tweets_collection = g.mongo_db["tweets"]
        return self._tweets_collection

    @property
    def twitter_client(self) -> tweepy.Client:
        """Lazy-loaded Twitter client."""
        if self._twitter_client is None:
            if not hasattr(g, 'twitter_client'):
                handle_logger(message="Twitter client not initialized", type_logger="error")
                raise RuntimeError("Twitter service unavailable")
            self._twitter_client = g.twitter_client
        return self._twitter_client

    def get_tweets(self, force_refresh: bool = False, search: str = '') -> List[Dict[str, Any]]:
        """Retrieve tweets, with caching and optional refresh."""
        try:
            if not force_refresh and self._has_cached_tweets():
                return self._get_cached_tweets()

            raw_tweets = self._fetch_from_twitter(search=search)
            
            if not raw_tweets:
                raise ValueError("No tweets received from Twitter API")

            processed_tweets = self._process_tweets(raw_tweets)
            self._store_tweets(processed_tweets)
            tweets = processed_tweets
            
            sorted_tweets = sorted(
                tweets,
                key=lambda x: x.get("created_at", datetime.min),
                reverse=True
            )
            
            for tweet in sorted_tweets:
                if '_id' in tweet:
                    tweet['_id'] = str(tweet['_id'])
                if 'created_at' in tweet and isinstance(tweet['created_at'], datetime):
                    tweet['created_at'] = tweet['created_at'].isoformat()
                if 'stored_at' in tweet and isinstance(tweet['stored_at'], datetime):
                    tweet['stored_at'] = tweet['stored_at'].isoformat()

            return sorted_tweets

        except (PyMongoError, tweepy.TweepyException) as e:
            handle_logger(message=f"Tweet service failed: {str(e)}", type_logger="error")
            raise RuntimeError("Tweet service operation failed") from e
        except Exception as e:
            handle_logger(message=f"Unexpected error in tweet service: {str(e)}", type_logger="error")
            raise

    def _has_cached_tweets(self) -> bool:
        """Check if there are any cached tweets in the database."""
        try:
            return self.tweets_collection.count_documents({}, limit=1) > 0
        except PyMongoError as e:
            handle_logger(message=f"Cache check failed: {str(e)}", type_logger="error")
            return False

    def _get_cached_tweets(self) -> List[Dict[str, Any]]:
        """Retrieve stored tweets, including new user fields."""
        try:
            tweets_cursor = self.tweets_collection.find(
                {},
                {
                    "_id": 1,
                    "tweet_id": 1,
                    "text": 1,
                    "author_id": 1,
                    "author_name": 1,
                    "author_photo": 1,
                    "created_at": 1,
                    "stored_at": 1,
                    "source": 1,
                    "processed": 1
                }
            )
            tweets = list(tweets_cursor)

            # Convert ObjectId and datetime fields
            for tweet in tweets:
                if "_id" in tweet:
                    tweet["_id"] = str(tweet["_id"])
                for field in ["created_at", "stored_at"]:
                    if field in tweet and isinstance(tweet[field], datetime):
                        tweet[field] = tweet[field].isoformat()
            return tweets
        except PyMongoError as e:
            handle_logger(message=f"Cache retrieval failed: {str(e)}", type_logger="error")
            return []

    def _fetch_from_twitter(self, search: str = '', max_retries: int = 1) -> List[Dict[str, Any]]:
        """ 
        Fetch tweets from Twitter API, acumulando resultados até `max_retries * 10` tweets (10 tweets por requisição).
        """
        tweets = []
        next_token = None
        attempts = 0
        
        while attempts < max_retries:
            try:
                response = self.twitter_client.search_recent_tweets(
                    query=f"{search} -is:retweet",
                    max_results=10,
                    tweet_fields=["text", "author_id", "created_at", "public_metrics"],
                    expansions=["author_id"],
                    user_fields=["name", "profile_image_url"],
                    next_token=next_token
                )

                if not response.data:
                    break

                users_map = {str(user.id): user for user in response.includes.get("users", [])}

                for tweet in response.data:
                    author_info = users_map.get(str(tweet.author_id))
                    metrics = tweet.public_metrics

                    tweets.append({
                        "tweet_id": tweet.id,
                        "text": tweet.text,
                        "author_id": tweet.author_id,
                        "author_name": author_info.name if author_info else "Unknown",
                        "author_photo": author_info.profile_image_url if author_info else "",
                        "created_at": tweet.created_at.isoformat() if tweet.created_at else datetime.utcnow().isoformat(),
                        "public_metrics": {
                            "like_count": int(metrics.get("like_count", 0)),
                            "retweet_count": int(metrics.get("retweet_count", 0)),
                            "reply_count": int(metrics.get("reply_count", 0)),
                            "quote_count": int(metrics.get("quote_count", 0)),
                            "bookmark_count": int(metrics.get("bookmark_count", 0)),
                            "impression_count": int(metrics.get("impression_count", 0))
                        },
                        "likes": int(metrics.get("like_count", 0)),
                        "retweets": int(metrics.get("retweet_count", 0)),
                        "replies": int(metrics.get("reply_count", 0))
                    })

                next_token = response.meta.get("next_token")

                if not next_token:
                    break

                attempts += 1
                sleep(1)

            except tweepy.TooManyRequests as e:
                retry_after = int(e.response.headers.get('Retry-After', 60))
                handle_logger(
                    message=f"Rate limited. Retrying in {retry_after}s (attempt {attempts + 1}/{max_retries})",
                    type_logger="warning"
                )
                sleep(retry_after)
                attempts += 1
            except tweepy.TweepyException as e:
                handle_logger(message=f"Twitter API error: {str(e)}", type_logger="error")
                raise
            except Exception as e:
                handle_logger(message=f"Unexpected error fetching tweets: {str(e)}", type_logger="error")
                raise

        return tweets

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
            tweet_copy["stored_at"] = current_time
            tweet_copy["source"] = "twitter_api"
            tweet_copy["processed"] = False
            tweet_copy["likes"] = tweet.get("likes", 0)
            tweet_copy["retweets"] = tweet.get("retweets", 0)
            tweet_copy["replies"] = tweet.get("replies", 0)
            tweet_copy["likes"] = int(tweet_copy.get("likes", 0))
            tweet_copy["retweets"] = int(tweet_copy.get("retweets", 0))
            tweet_copy["replies"] = int(tweet_copy.get("replies", 0))\
            
            if isinstance(tweet_copy.get("created_at"), str):
                try:
                    tweet_copy["created_at"] = datetime.fromisoformat(tweet_copy["created_at"].replace("Z", "+00:00"))
                except ValueError:
                    tweet_copy["created_at"] = datetime.utcnow()

            processed.append(tweet_copy)
        return processed

    def _store_tweets(self, tweets: List[Dict[str, Any]]) -> None:
        """Store processed tweets in MongoDB, including engagement metrics."""
        if not tweets:
            handle_logger(message="No tweets to store", type_logger="warning")
            return

        try:
            result = self.tweets_collection.insert_many(
                tweets,
                ordered=False,
                bypass_document_validation=False
            )
            handle_logger(message=f"Stored {len(result.inserted_ids)}/{len(tweets)} new tweets", type_logger="info")
        except DuplicateKeyError as e:
            handle_logger(message=f"Duplicate tweets detected and skipped: {str(e)}", type_logger="warning")
        except PyMongoError as e:
            handle_logger(message=f"Storage failed: {str(e)}", type_logger="error")
            raise

    def process_hourly_metrics(self, force_refresh: bool = False, search: str = '') -> Dict[str, Any]:
        """
        Calculate and store hourly tweet metrics, including engagement and hype score.

        Parameters:
        - force_refresh (bool): Forces new tweet retrieval.
        - search (str): Search term for filtering tweets.

        Returns:
        - dict: Contains hourly metrics, processed tweets, and sentiment analysis.
        """
        try:
            tweets = self.get_tweets(force_refresh=force_refresh, search=search)
            if not tweets:
                raise ValueError("No tweets available for metrics analysis")

            hourly_stats = analytic_tweets(tweets)
            if hourly_stats.empty:
                raise ValueError("No hourly stats received")

            hourly_stats_list = hourly_stats.to_dict("records")
            hype_scores = calculate_hype_score(hourly_stats_list)

            total_tweets = len(tweets)

            # Initialize aggregated metrics
            total_likes = sum(tweet.get("likes", 0) for tweet in tweets)
            total_retweets = sum(tweet.get("retweets", 0) for tweet in tweets)
            total_replies = sum(tweet.get("replies", 0) for tweet in tweets)

            # Compute means safely (avoid division by zero)
            likes_mean = total_likes / total_tweets if total_tweets > 0 else 0
            retweets_mean = total_retweets / total_tweets if total_tweets > 0 else 0
            replies_mean = total_replies / total_tweets if total_tweets > 0 else 0

            # Process hourly stats with engagement and hype scores
            for record in hourly_stats_list:
                hour = int(record.get("hour"))

                # Add engagement metrics
                record["likes_mean"] = likes_mean
                record["retweets_mean"] = retweets_mean
                record["replies_mean"] = replies_mean

                # Add hype score
                hype = next((h for h in hype_scores if int(h["hour"]) == int(hour)), {"hype_score": 0})
                record["hype_score"] = hype["hype_score"]

                # Perform single database update per document
                self.metrics_collection.update_one(
                    {"hour": hour},
                    {"$set": record},
                    upsert=True
                )

            handle_logger(message="✅ Hourly metrics saved successfully.", type_logger="info")

            # Retrieve updated metrics
            all_metrics_cursor = self.metrics_collection.find({}, {"_id": 0})
            all_metrics = list(all_metrics_cursor)

            # Process tweet sentiments
            feelings = process_tweet(tweets)

            return {"metrics": all_metrics, "tweets": tweets, "feelings": feelings}

        except Exception as e:
            handle_logger(message=f"❌ Error saving hourly metrics: {str(e)}", type_logger="error")
            raise