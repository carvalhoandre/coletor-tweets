import pandas as pd
from flask import current_app
from preprocess.tweets_preprocess import process_tweet

from utils.logger import handle_logger

def analytic_tweets(raw_tweets: list):
    """
    Analyzes a list of raw tweets and calculates various metrics per hour.

    Metrics calculated:
    - Average sentiment per hour
    - Number of tweets per hour
    - Average likes per hour
    - Average retweets per hour
    - Average replies per hour
    - Average shares per hour

    Parameters:
    - raw_tweets: List of dictionaries with at least the keys "text", "created_at", and optionally "public_metrics"

    Returns:
    - A DataFrame with hourly metrics
    """
    try:
        processed_tweets = process_tweet(raw_tweets)
        df = pd.DataFrame(processed_tweets)

        if df.empty:
            handle_logger(message=f"No tweets available for analysis.", type_logger="warning")
            return pd.DataFrame()

        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        df['hour'] = df['timestamp'].dt.hour

        if 'sentiment' not in df.columns:
            raise ValueError("Processed tweets do not have the 'sentiment' column'")

        required_columns = ['sentiment', 'likes', 'retweets', 'replies']
        for col in required_columns:
            if col not in df.columns:
                handle_logger(message=f"⚠️ Missing column: {col}. Filling with zeros.", type_logger="warning")
                df[col] = 0

        df['likes'] = df['likes'].fillna(0).astype(int)
        df['retweets'] = df['retweets'].fillna(0).astype(int)
        df['replies'] = df['replies'].fillna(0).astype(int)
        df['sentiment'] = df['sentiment'].fillna(0).astype(float)

        # Group by hour and compute metrics
        hourly_stats = df.groupby('hour').agg(
            sentiment_mean=('sentiment', 'mean'),
            tweet_count=('text', 'count'),
            likes_mean=('likes', 'mean'),
            retweets_mean=('retweets', 'mean'),
            replies_mean=('replies', 'mean')
        ).reset_index()

        handle_logger(message="✅ Hourly metrics computed successfully.", type_logger="info")

        return hourly_stats
    except Exception as e:
        handle_logger(message=f"Error analyzing tweets: {str(e)}", type_logger="error")
        raise
