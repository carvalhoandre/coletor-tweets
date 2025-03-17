from functools import wraps

from flask import jsonify
from werkzeug.exceptions import HTTPException
import traceback
import logging

from utils.logger import handle_logger
from utils.response_http_util import standard_response

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

def handle_exception(e):
    """
    Handles both HTTP exceptions and unexpected errors gracefully.

    Returns:
        - JSON response with {"success": False, "message": "..."}
        - Proper HTTP status codes
    """
    if isinstance(e, HTTPException):
        response = {
            "success": False,
            "message": e.description or "A known error occurred",
        }
        return jsonify(response), e.code or 500

    # Log unexpected errors with traceback
    error_trace = traceback.format_exc()
    logger.error(f"Unexpected server error: {str(e)}\n{error_trace}")

    response = {
        "success": False,
        "message": "An unexpected server error occurred. Please try again later.",
    }
    return jsonify(response), 500

def handle_exceptions(route_function):
    """
    Decorator to handle exceptions and reduce repetitive try-except blocks in routes.
    """
    @wraps(route_function)
    def wrapper(*args, **kwargs):
        try:
            return route_function(*args, **kwargs)
        except ValueError as ve:
            handle_logger(message=f"ValueError: {str(ve)}", type_logger="error")
            return standard_response(False, str(ve), 400)
        except Exception as e:
            handle_logger(message=f"Unexpected error: {str(e)}", type_logger="error")
            return standard_response(False, "Internal error", 500)
    return wrapper