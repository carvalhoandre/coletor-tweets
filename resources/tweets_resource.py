from flask import Blueprint, request
from preprocess.tweets_preprocess import process_tweet
from utils.error_handler import handle_exceptions
from utils.params import get_query_params

from utils.response_http_util import standard_response
from services.tweets_service import TweetService

tweets_bp = Blueprint('tweets', __name__)
tweet_service = TweetService()

@tweets_bp.route('/fetch_tweets', methods=['GET'])
@handle_exceptions
def fetch_tweets():
    """Fetch tweets and return them as a JSON response"""
    force_refresh, search = get_query_params()
    if search is None:
        return search

    tweets = tweet_service.get_tweets(force_refresh=force_refresh, search=search)
    if not tweets:
        return standard_response(False, "No tweets available", 404)

    return standard_response(True, "Tweets retrieved", 200, tweets)

@tweets_bp.route('/feelings', methods=['GET'])
@handle_exceptions
def get_feelings():
    """Fetch tweets and process feelings return them as a JSON response"""
    force_refresh, search = get_query_params()
    if search is None:
        return search

    tweets = tweet_service.get_tweets(force_refresh=force_refresh, search=search)
    if not tweets:
        return standard_response(False, "No tweets available", 404)

    feelings = process_tweet(tweets)
    return standard_response(True, "Feelings retrieved", 200, feelings)

@tweets_bp.route('/hourly_metrics', methods=['GET'])
@handle_exceptions
def hourly_metrics():
    """Fetch tweets and process hourly metrics return them as a JSON response"""
    force_refresh, search = get_query_params()
    if search is None:
        return search

    metrics = tweet_service.process_hourly_metrics(force_refresh=force_refresh, search=search)
    if not metrics:
        return standard_response(False, "No tweets available", 404)

    return standard_response(True, "Hourly metrics retrieved", 200, metrics)
