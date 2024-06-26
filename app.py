# app.py

import logging
from flask import Flask, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from bridge_status import fetch_bridge_status, get_current_bridge_status
from bridge_stats import bridge_stats
from utils import require_api_key
from config import FETCH_INTERVAL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/bridge-status', methods=['GET'])
@require_api_key
def get_bridge_status():
    return jsonify(get_current_bridge_status())

@app.route('/stats', methods=['GET'])
@require_api_key
def get_bridge_statistics():
    return jsonify(bridge_stats.get_filtered_stats())

@app.route('/history', methods=['GET'])
@require_api_key
def get_bridge_history():
    return jsonify(bridge_stats.get_filtered_history())

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

def init_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(fetch_bridge_status, 'interval', seconds=FETCH_INTERVAL)
    scheduler.start()
    return scheduler

if __name__ == '__main__':
    scheduler = init_scheduler()
    fetch_bridge_status()  # Fetch initial data
    
    try:
        app.run(host='0.0.0.0', port=5000)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()