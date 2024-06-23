from flask import Flask, jsonify, request
from apscheduler.schedulers.background import BackgroundScheduler
from bridge_status import fetch_bridge_status, get_current_bridge_status
from utils import require_api_key
from config import FETCH_INTERVAL

app = Flask(__name__)

@app.route('/bridge-status', methods=['GET'])
@require_api_key
def get_bridge_status():
    return jsonify(get_current_bridge_status())

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
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()