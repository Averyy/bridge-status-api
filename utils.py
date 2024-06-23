import re
from functools import wraps
from flask import jsonify, request
from config import API_KEY

def require_api_key(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        if request.headers.get('X-API-Key') and request.headers.get('X-API-Key') == API_KEY:
            return view_function(*args, **kwargs)
        else:
            return jsonify({"error": "Unauthorized"}), 401
    return decorated_function

def clean_action_status(status):
    if status:
        cleaned_status = re.sub(r' since \d{2}:\d{2}', '', status).strip()
        return cleaned_status
    return status

def parse_status(status):
    match = re.match(r'(.*?)(?:\s*\((.*?)\))?$', status)
    if match:
        current_status = match.group(1).strip()
        action_status = match.group(2) if match.group(2) else None
        action_status = clean_action_status(action_status)
        return current_status, action_status
    return status, None