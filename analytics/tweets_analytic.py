import pandas as pd
from flask import current_app
from preprocess.tweets_preprocess import process_tweet

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
            current_app.logger.warning("No tweets available for analysis.")
            return pd.DataFrame()

        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        df['hour'] = df['timestamp'].dt.hour

        if 'sentiment' not in df.columns:
            raise ValueError("Processed tweets do not have the 'sentiment' column'")

        df['likes'] = df.get('likes', 0)
        df['retweets'] = df.get('retweets', 0)
        df['replies'] = df.get('replies', 0)
        df['shares'] = df.get('shares', 0)

        # Group by hour and compute metrics
        hourly_stats = df.groupby('hour').agg(
            sentiment_mean=('sentiment', 'mean'),
            tweet_count=('text', 'count'),
            likes_mean=('likes', 'mean'),
            retweets_mean=('retweets', 'mean'),
            replies_mean=('replies', 'mean'),
            shares_mean=('shares', 'mean')
        ).reset_index()

        return hourly_stats
    except Exception as e:
        current_app.logger.error(f"Error analyzing tweets: {str(e)}")
        raise
