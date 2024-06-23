import os
import pytz

URL = os.getenv('BRIDGE_STATUS_URL', 'https://seaway-greatlakes.com/bridgestatus/detailsnai?key=BridgeSCT')
FETCH_INTERVAL = int(os.getenv('FETCH_INTERVAL', 30))
API_KEY = os.getenv('API_KEY', 'your_secret_api_key_here')
# Local should be in the same timezone as the bridges
local_tz = pytz.timezone('America/Toronto')