from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import logging
import os
from functools import wraps

app = Flask(__name__)
bridge_status = []

# Configure logging
logging.basicConfig(level=logging.INFO)

# Configuration from environment variables
URL = os.getenv('BRIDGE_STATUS_URL', 'https://seaway-greatlakes.com/bridgestatus/detailsnai?key=BridgeSCT')
FETCH_INTERVAL = int(os.getenv('FETCH_INTERVAL', 30))
API_KEY = os.getenv('API_KEY')

def require_api_key(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        if request.headers.get('X-API-Key') and request.headers.get('X-API-Key') == API_KEY:
            return view_function(*args, **kwargs)
        else:
            return jsonify({"error": "Unauthorized"}), 401
    return decorated_function

def fetch_bridge_status():
    global bridge_status
    try:
        response = requests.get(URL)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        bridge_tables = soup.find_all('table', {'id': 'grey_box'})

        updated_status = []
        for idx, table in enumerate(bridge_tables, 1):
            bridge_name = table.find('span', {'class': 'lgtextblack'}).text.strip()
            status = table.find('span', {'id': 'status'}).text.strip()
            colour_img = table.find('img')['src']
            colour = colour_img.split('/')[-1].split('.')[0]  # Extract colour from image name

            updated_status.append({
                'id': idx,'location': bridge_name,
                'status': status,
                'colour': colour,
                'last_updated': datetime.now().isoformat()
            })

        bridge_status = updated_status
        logging.info("Bridge status updated successfully.")
    except Exception as e:
        logging.error(f"Error fetching bridge status: {e}")

@app.route('/bridge-status', methods=['GET'])
@require_api_key
def get_bridge_status():
    return jsonify({'bridges': bridge_status})

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(fetch_bridge_status, 'interval', seconds=FETCH_INTERVAL)
    scheduler.start()
    fetch_bridge_status()

    try:
        app.run(host='0.0.0.0', port=5000)
    except (KeyboardInterrupt, SystemExit):scheduler.shutdown()