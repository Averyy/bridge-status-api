import re
from datetime import datetime
import pytz
import requests
from bs4 import BeautifulSoup
from config import URL, local_tz
from utils import parse_status

bridge_status = []
bridge_data = {}

def get_current_time():
    return datetime.now(pytz.utc).astimezone(local_tz)

def fetch_bridge_status():
    global bridge_status
    try:
        response = requests.get(URL)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        bridge_tables = soup.find_all('table', {'id': 'grey_box'})
        last_updated = get_current_time()
        updated_status = []
        for idx, table in enumerate(bridge_tables, 1):
            bridge_name = table.find('span', {'class': 'lgtextblack'}).text.strip()
            status = table.find('span', {'id': 'status'}).text.strip()
            current_status, action_status = parse_status(status)
            
            time_match = re.search(r'since (\d{2}:\d{2})', status)
            if time_match:
                time_str = time_match.group(1)
                bridge_time = datetime.strptime(time_str, '%H:%M').time()
                bridge_datetime = datetime.combine(last_updated.date(), bridge_time)
                new_bridge_last_updated = local_tz.localize(bridge_datetime)
            else:
                new_bridge_last_updated = last_updated

            if idx not in bridge_data:
                bridge_data[idx] = {
                    'last_known_update': new_bridge_last_updated,
                    'previous_status': current_status,
                    'previous_action_status': action_status
                }
            else:
                status_changed = bridge_data[idx]['previous_status'] != current_status
                action_changed = bridge_data[idx]['previous_action_status'] != action_status
                
                if status_changed or action_changed:
                    bridge_data[idx]['last_known_update'] = new_bridge_last_updated
                    bridge_data[idx]['previous_status'] = current_status
                    bridge_data[idx]['previous_action_status'] = action_status
                elif time_match:
                    bridge_data[idx]['last_known_update'] = new_bridge_last_updated

            bridge_last_updated = bridge_data[idx]['last_known_update']
            bridge_last_updated_iso = bridge_last_updated.isoformat()
            bridge_data_entry = {
                'id': idx,
                'location': bridge_name,
                'status': current_status,
                'action': action_status,
                'updated': bridge_last_updated_iso
            }
            updated_status.append(bridge_data_entry)

        bridge_status = {
            'updated': last_updated.isoformat(),
            'bridges': updated_status
        }
    except Exception as e:
        print(f"Error fetching bridge status: {e}")

def get_current_bridge_status():
    return bridge_status.copy()