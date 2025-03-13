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
        text = tweet.get("text", "")
        cleaned_tweet = clean_text(text)
        sentiment = sia.polarity_scores(cleaned_tweet)["compound"]

        # Extração segura de valores adicionais
        tweet_id = tweet.get("tweet_id", "unknown")
        author_id = tweet.get("author_id", "unknown")
        author_name = tweet.get("author_name", "Unknown")
        author_photo = tweet.get("author_photo", "")
        created_at = tweet.get("created_at", "")

        # Convertendo timestamp para datetime (caso necessário)
        if isinstance(created_at, str):
            try:
                timestamp = datetime.fromisoformat(created_at)
            except ValueError:
                timestamp = None
        else:
            timestamp = created_at

        # Extraindo métricas de engajamento **com verificação**
        public_metrics = tweet.get("public_metrics", {})
        likes = public_metrics.get("like_count", 0) if isinstance(public_metrics, dict) else 0
        retweets = public_metrics.get("retweet_count", 0) if isinstance(public_metrics, dict) else 0
        replies = public_metrics.get("reply_count", 0) if isinstance(public_metrics, dict) else 0
        shares = public_metrics.get("quote_count", 0) if isinstance(public_metrics, dict) else 0  # Considerando "quote_count" como compartilhamentos

        processed_tweets.append({
            "tweet_id": tweet_id,
            "text": text,
            "cleaned_text": cleaned_tweet,
            "sentiment": sentiment,
            "timestamp": timestamp.isoformat() if timestamp else None,
            "author_id": author_id,
            "author_name": author_name,
            "author_photo": author_photo,
            "likes": likes,
            "retweets": retweets,
            "replies": replies,
            "shares": shares
        })

    return processed_tweets
