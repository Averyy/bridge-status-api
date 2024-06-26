# config.py

import os
import pytz

# Bridge status URL
URL = os.getenv('BRIDGE_STATUS_URL', 'https://seaway-greatlakes.com/bridgestatus/detailsnai?key=BridgeSCT')

# Fetch interval in seconds
FETCH_INTERVAL = int(os.getenv('FETCH_INTERVAL', 30))

# API key for authentication
API_KEY = os.getenv('API_KEY', 'your_secret_api_key_here')

# Local timezone (Toronto time) used in utils.py
TORONTO_TZ = pytz.timezone('America/Toronto')

# History storage. If unset use root dir
BRIDGE_STATS_FILE = os.getenv('BRIDGE_STATS_FILE', 'bridge_stats.json')