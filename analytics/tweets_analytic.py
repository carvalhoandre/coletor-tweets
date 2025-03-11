import pandas as pd
from flask import current_app

from preprocess.tweets_preprocess import process_tweet

def analytic_tweets(raw_tweets: list):
    """
    Analytic a list of raw tweets, get the average feelings per hour.
    Save the average feelings per hour.

    Parameters:
    - raw_tweets: List of dictionaries with at least the keys "text" and "created_at"

    Returns:
    - A list of dictionaries with the fields "text", "sentiment" and "timestamp"
    """
    try:
        processed_tweets = process_tweet(raw_tweets)

        df = pd.DataFrame(processed_tweets)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.hour

        if 'sentiment' not in df.columns:
            raise ValueError("Processed tweets do not have the 'sentiment' column'")

        hourly_stats = df.groupby('hour')['sentiment'].mean().reset_index()

        return hourly_stats
    except Exception as e:
        current_app.logger.error(f"Error analytics tweets: {str(e)}")
        raise