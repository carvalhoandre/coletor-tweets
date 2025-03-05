from flask import jsonify

def standard_response(success, message, status_code, data=None):
    response = {
        "success": success,
        "message": message,
    }
    if data is not None:
        response["data"] = data
    return jsonify(response), status_code
