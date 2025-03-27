from typing import Any, Dict, List
import nltk
import re
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from datetime import datetime

nltk.download('vader_lexicon')

def clean_text(text: str) -> str:
    """Remove mentions, hashtags, and URLs from text."""
    if not text:
        return ""
    text = re.sub(r"@\w+|#\w+", "", text)  # Remove mentions and hashtags
    text = re.sub(r"http\S+", "", text)    # Remove URLs
    return text.strip()

def process_tweet(raw_tweets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Processes a list of raw tweets, cleaning the text, classifying the sentiment,
    and preserving important metadata.

    Parameters:
    - raw_tweets: List of dictionaries with at least the keys "text" and "created_at"

    Returns:
    - A list of dictionaries with:
      - "tweet_id", "text", "cleaned_text", "sentiment", "timestamp"
      - "author_id", "author_name", "author_photo"
      - "likes", "retweets", "replies", "shares"
    """
    sia = SentimentIntensityAnalyzer()
    processed_tweets = []

    for tweet in raw_tweets:
        text = tweet.get("text", "").strip()
        cleaned_tweet = clean_text(text)
        sentiment = sia.polarity_scores(cleaned_tweet)["compound"]

        # Ensure valid timestamps
        created_at = tweet.get("created_at")
        timestamp = None
        if isinstance(created_at, str):
            try:
                timestamp = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            except ValueError:
                timestamp = None

        # Extract author information
        processed_tweet = {
            "tweet_id": tweet.get("tweet_id", "unknown"),
            "text": text,
            "cleaned_text": cleaned_tweet,
            "sentiment": sentiment,
            "timestamp": timestamp if timestamp else datetime.utcnow(),
            "author_id": tweet.get("author_id", "unknown"),
            "author_name": tweet.get("author_name", "Unknown"),
            "author_photo": tweet.get("author_photo", ""),
        }

        # Extract engagement metrics safely
        public_metrics = tweet.get("public_metrics", {})
        processed_tweet["likes"] = public_metrics.get("like_count", 0)
        processed_tweet["retweets"] = public_metrics.get("retweet_count", 0)
        processed_tweet["replies"] = public_metrics.get("reply_count", 0)
        processed_tweet["shares"] = public_metrics.get("quote_count", 0)

        processed_tweets.append(processed_tweet)

    return processed_tweets
