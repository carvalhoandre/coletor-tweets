from flask import Blueprint, current_app, request
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