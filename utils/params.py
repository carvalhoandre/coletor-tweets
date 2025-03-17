from flask import request
from utils.response_http_util import standard_response

def get_query_params():
    """Extracts and validates query parameters from request."""
    force_refresh = request.args.get('force_refresh', "false").lower() == "true"
    search = request.args.get('search', "").strip().lower()

    if not search:
        return None, standard_response(False, "Missing 'search' parameter", 400)

    return force_refresh, search