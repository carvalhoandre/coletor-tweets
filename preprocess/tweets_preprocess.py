from typing import Any

import nltk

nltk.download('vader_lexicon')

from nltk.sentiment.vader import SentimentIntensityAnalyzer
import re


def clean_text(text):
    """
    Clear text and remove mentions, hashtags  and URLs
    """
    text = re.sub(r"@\w+|#\w+", "", text)  # Remove mentions and hashtags
    text = re.sub(r"http\S+", "", text)     # Remove URLs
    return text.strip()

def process_tweet(raw_tweets: list) -> list[dict[str, str | Any]] | None:
    """
    Processes a list of raw tweets, cleaning the text and classifying the sentiment.

    Parameters:
    - raw_tweets: List of dictionaries with at least the keys "text" and "created_at"

    Returns:
    - A list of dictionaries with the fields "text", "sentiment" and "timestamp"
    """
    sia = SentimentIntensityAnalyzer()
    processed_tweets = []

    for tweet in raw_tweets:
        cleaned_tweet = clean_text(tweet.get("text", ""))
        sentiment = sia.polarity_scores(cleaned_tweet)["compound"]
        processed_tweets.append({"text": cleaned_tweet, "sentiment": sentiment, "timestamp": tweet["created_at"]})

    return processed_tweets
