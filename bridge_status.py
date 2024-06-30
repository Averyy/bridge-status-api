# bridge_status.py

import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime, timedelta
from config import URL
from bridge_stats import bridge_stats
from utils import parse_status, get_current_time

logger = logging.getLogger(__name__)

bridge_status = []

def format_display_data(current_status, action_status, current_time, bridge_stat):
    last_status_change = datetime.fromisoformat(bridge_stat['last_status_change'])
    time_format = "%-I:%M%p"  # For Unix-based systems
    # time_format = "%#I:%M%p"  # Uncomment this line for Windows systems

    def format_time(dt):
        return dt.strftime(time_format).lower()

    if current_status == "Available":
        if action_status == "Raising Soon":
            display_status = "OPEN"
            icon = "checkmarkWarning"
            avg_raising_time = bridge_stat.get("avg_raising_soon_to_unavailable", 0)
            raising_soon_ci = bridge_stat.get("raising_soon_ci", (0, 0))
            if avg_raising_time:
                time_since_change = (current_time - last_status_change).total_seconds() / 60
                lower_remaining = max(0, int(raising_soon_ci[0] - time_since_change))
                upper_remaining = max(0, int(raising_soon_ci[1] - time_since_change))
                if upper_remaining > 1:
                    display_details = f"Closing soon in {lower_remaining}-{upper_remaining}m (avg)"
                else:
                    display_details = "Closing soon (longer than usual)"
            else:
                display_details = "Closing soon"
        else:
            display_status = "OPEN"
            icon = "checkmark"
            display_details = f"Opened {format_time(last_status_change)}"
    elif current_status == "Unavailable":
        if action_status == "Raising":
            display_status = "CLOSING"
            icon = "warning"
            display_details = f"Closed {format_time(last_status_change)}"
        elif action_status == "Lowering":
            display_status = "OPENING"
            icon = "clock"
            display_details = "Opening right now..."
        elif action_status and "Fully Raised since" in action_status:
            display_status = "CLOSED"
            icon = "warning"
            closure_start = datetime.fromisoformat(bridge_stat["closures"][-1]["start"]) if bridge_stat["closures"] else last_status_change
            fully_raised_time = datetime.strptime(action_status.split("since")[-1].strip(), "%H:%M").replace(year=current_time.year, month=current_time.month, day=current_time.day)
            display_details = f"Closed {format_time(closure_start)}, fully raised since {format_time(fully_raised_time)}"
        else:
            display_status = "CLOSED"
            icon = "warning"
            closure_start = datetime.fromisoformat(bridge_stat["closures"][-1]["start"]) if bridge_stat["closures"] else last_status_change
            avg_closure_time = bridge_stat.get("avg_closure_duration", 0)
            closure_duration_ci = bridge_stat.get("closure_duration_ci", (0, 0))
            if avg_closure_time:
                time_closed = (current_time - closure_start).total_seconds() / 60
                lower_remaining = max(0, int(closure_duration_ci[0] - time_closed))
                upper_remaining = max(0, int(closure_duration_ci[1] - time_closed))
                if upper_remaining > 1:
                    display_details = f"Closed {format_time(closure_start)}. Open in {lower_remaining}-{upper_remaining}m (avg)"
                else:
                    display_details = f"Closed {format_time(closure_start)} for longer than usual"
            else:
                display_details = f"Closed {format_time(closure_start)}"

    else:
        # Handle unknown or new statuses
        if "Available" in current_status:
            display_status = "OPEN"
            icon = "checkmark"
        elif "Unavailable" in current_status:
            display_status = "CLOSED"
            icon = "warning"
        else:
            display_status = "UNKNOWN"
            icon = "question"
        
        display_details = current_status
        if action_status:
            display_details += f" ({action_status})"

    return display_status, display_details, icon

def fetch_bridge_status():
    global bridge_status
    try:
        logger.info("Fetching bridge status")
        response = requests.get(URL)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        bridge_tables = soup.find_all('table', {'id': 'grey_box'})
        
        last_updated = get_current_time()
        updated_status = []
        
        for idx, table in enumerate(bridge_tables, 1):
            try:
                bridge_name = table.find('span', {'class': 'lgtextblack'}).text.strip()
                status = table.find('span', {'id': 'status'}).text.strip()
                
                logger.info(f"Raw Bridge {idx}: {bridge_name}, status: {status}")
                current_status, action_status = parse_status(status)
                logger.info(f"Parsed Bridge {idx}: {bridge_name}, current_status='{current_status}', action_status='{action_status}'")
                
                bridge_data = bridge_stats.get_bridge_stat(idx)
                if not bridge_data:
                    bridge_data = bridge_stats.create_new_bridge_stat(idx, bridge_name, current_status, last_updated)
                
                bridge_stats.update_bridge_stat(idx, bridge_name, current_status, action_status, last_updated)
                
                display_status, display_details, icon = format_display_data(current_status, action_status, last_updated, bridge_data)
                
                bridge_data_entry = {
                    'id': idx,
                    'location': bridge_name,
                    'state': display_status,
                    'info': display_details,
                    'icon': icon
                }
                updated_status.append(bridge_data_entry)
            except Exception as e:
                logger.error(f"Error processing bridge {idx}: {str(e)}", exc_info=True)

        bridge_status = {
            'updated': last_updated.isoformat(),
            'bridges': updated_status
        }
        logger.info("Updated bridge_status")

    except Exception as e:
        logger.error(f"Error fetching bridge status: {str(e)}", exc_info=True)

def get_current_bridge_status():
    return bridge_status