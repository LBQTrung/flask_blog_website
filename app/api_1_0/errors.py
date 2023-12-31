from flask import jsonify
from . import api


def bad_request(message):
    response = jsonify({"error": "bad request", "message": message})
    response.status_code = 400
    return response


def forbidden(message):
    response = jsonify({"error": "forbidden", "message": message})
    response.status_code = 403
    return response
