import os
import tweepy
from flask import g, current_app


def get_twitter_client():
    """Initialize and cache Twitter client in Flask's g object"""
    if 'twitter_client' not in g:
        try:
            # Get from app config instead of direct env access
            bearer_token = os.getenv("BEARER_TOKEN")

            if not bearer_token:
                raise RuntimeError("Twitter credentials not configured")

            g.twitter_client = tweepy.Client(
                bearer_token=bearer_token,
                wait_on_rate_limit=True
            )
            current_app.logger.info("✅ Twitter client initialized")

        except tweepy.TweepyException as e:
            current_app.logger.error(f"Twitter client error: {str(e)}")
            raise
        except Exception as e:
            current_app.logger.error(f"Twitter config error: {str(e)}")
            raise

    return g.twitter_client


def close_twitter_client(e=None):
    """Optional cleanup (not needed for tweepy.Client)"""
    client = g.pop('twitter_client', None)
    if client is not None:
        pass