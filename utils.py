# utils.py

from functools import wraps
from flask import jsonify, request
from config import API_KEY, TORONTO_TZ
from datetime import datetime
import re

def require_api_key(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        if request.headers.get('X-API-Key') and request.headers.get('X-API-Key') == API_KEY:
            return view_function(*args, **kwargs)
        else:
            return jsonify({"error": "Unauthorized"}), 401
    return decorated_function

def parse_status(status):
    status_pattern = re.compile(r'(Available|Unavailable)(?:\s*\((.*?)\))?')
    match = status_pattern.match(status)
    if match:
        current_status = match.group(1)
        action_status = match.group(2) if match.group(2) else None
        if action_status:
            # Remove leading/trailing dashes and whitespace
            action_status = re.sub(r'^-*\s*|\s*-*$', '', action_status)
            if "since" in action_status:
                action_status = action_status.split("since")[0].strip()
        return current_status, action_status
    return status, None

def get_current_time():
    return datetime.now(TORONTO_TZ)