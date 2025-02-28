from flask import jsonify
from werkzeug.exceptions import HTTPException

def handle_exception(e):
    if isinstance(e, HTTPException):
        return jsonify({
            "success": False,
            "message": e.description
        }), e.code

    return jsonify({
        "success": False,
        "message": "An unexpected error occurred"
    }), 500
