from flask import Blueprint, current_app, request
from preprocess.tweets_preprocess import process_tweet
from utils.response_http_util import standard_response
from services.tweets_service import TweetService

tweets_bp = Blueprint('tweets', __name__)

tweet_service = TweetService()

@tweets_bp.route('/fetch_tweets', methods=['GET'])
def fetch_tweets():
    """Fetch tweets and return them as a JSON response"""
    try:
        force_refresh = request.args.get('force_refresh', "false").lower() == "true"
        tweets = tweet_service.get_tweets(force_refresh=force_refresh)

        if not tweets:
            return standard_response(False, "No tweets available", 404)

        return standard_response(True, "Tweets retrieved", 200, tweets)

    except ValueError as ve:
        current_app.logger.error(f"ValueError: {str(ve)}")
        return standard_response(False, str(ve), 400)

    except Exception as e:
        current_app.logger.error(f"Unexpected error: {str(e)}")
        return standard_response(False, "Internal error", 500)

@tweets_bp.route('/feelings', methods=['GET'])
def get_feelings():
    """Fetch tweets and process feelings return them as a JSON response"""
    try:
        force_refresh = request.args.get('force_refresh', "false").lower() == "true"
        tweets = tweet_service.get_tweets(force_refresh=force_refresh)

        if not tweets:
            return standard_response(False, "No tweets available", 404)

        feelings = process_tweet(tweets)

        return standard_response(True, "Feelings retrieved", 200, feelings)

    except ValueError as ve:
        current_app.logger.error(f"ValueError: {str(ve)}")
        return standard_response(False, str(ve), 400)

    except Exception as e:
        current_app.logger.error(f"Unexpected error: {str(e)}")
        return standard_response(False, "Internal error", 500)

@tweets_bp.route('/hourly_metrics', methods=['GET'])
def hourly_metrics():
    """Fetch tweets and process hourly_metrics return them as a JSON response"""
    try:
        force_refresh = request.args.get('force_refresh', "false").lower() == "true"
        metrics = tweet_service.process_hourly_metrics(force_refresh=force_refresh)

        if not metrics:
            return standard_response(False, "No tweets available", 404)

        return standard_response(True, "Feelings retrieved", 200, metrics)

    except ValueError as ve:
        current_app.logger.error(f"ValueError: {str(ve)}")
        return standard_response(False, str(ve), 400)

    except Exception as e:
        current_app.logger.error(f"Unexpected error: {str(e)}")
        return standard_response(False, "Internal error", 500)
    