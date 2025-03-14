import os
import tweepy
from flask import g, current_app

from utils.looger import handle_logger

def get_twitter_client():
    """Initialize and cache Twitter client in Flask's g object."""
    if 'twitter_client' not in g:
        try:
            bearer_token = os.getenv("BEARER_TOKEN")
            if not bearer_token:
                raise RuntimeError("Twitter credentials not configured")

            g.twitter_client = tweepy.Client(
                bearer_token=bearer_token,
                wait_on_rate_limit=True
            )

            handle_logger(message="✅ Twitter client initialized", type_logger="info")
        except tweepy.TweepyException as e:
            handle_logger(message=f"❌ Twitter client error: {str(e)}", type_logger="error")
            raise
        except Exception as e:
            handle_logger(message=f"⚠️ Twitter config error: {str(e)}", type_logger="error")
            raise

    return g.twitter_client

def close_twitter_client(e=None):
    """Cleanup function to remove Twitter client from Flask's global object (g)."""
    client = g.pop('twitter_client', None)
    if client is not None:
        handle_logger(message="🔄 Twitter client removed from g", type_logger="info")
