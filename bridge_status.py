# bridge_status.py

import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime, timedelta
from config import URL, TORONTO_TZ
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
            display_status = "OPEN NOW"
            avg_raising_time = bridge_stat.get("avg_raising_soon_to_unavailable", 0)
            if avg_raising_time:
                time_since_change = (current_time - last_status_change).total_seconds() / 60
                remaining_time = max(1, int(avg_raising_time - time_since_change))
                display_details = f"Closing in {remaining_time}m"
            else:
                display_details = "Closing soon"
        else:
            display_status = "OPEN NOW"
            display_details = f"Opened {format_time(last_status_change)}"
    elif current_status == "Unavailable":
        if action_status == "Raising":
            display_status = "CLOSING..."
            display_details = f"Closed {format_time(last_status_change)}"
        elif action_status == "Lowering":
            display_status = "OPENING..."
            display_details = "Opening right now..."
        elif action_status == "Lowering Soon":
            display_status = "OPEN SOON"
            avg_lowering_time = bridge_stat.get("avg_lowering_soon_to_available", 0)
            if avg_lowering_time:
                time_since_change = (current_time - last_status_change).total_seconds() / 60
                remaining_time = max(1, int(avg_lowering_time - time_since_change))
                display_details = f"Opening in {remaining_time}m"
            else:
                display_details = "Opening soon"
        elif action_status and "Fully Raised since" in action_status:
            display_status = "CLOSED NOW"
            closure_start = datetime.fromisoformat(bridge_stat["closures"][-1]["start"]) if bridge_stat["closures"] else last_status_change
            fully_raised_time = datetime.strptime(action_status.split("since")[-1].strip(), "%H:%M").replace(year=current_time.year, month=current_time.month, day=current_time.day)
            display_details = f"Closed {format_time(closure_start)}, fully raised since {format_time(fully_raised_time)}"
        else:
            display_status = "CLOSED NOW"
            closure_start = datetime.fromisoformat(bridge_stat["closures"][-1]["start"]) if bridge_stat["closures"] else last_status_change
            avg_closure_time = bridge_stat.get("avg_closure_duration", 0)
            if avg_closure_time:
                estimated_open_time = closure_start + timedelta(minutes=avg_closure_time)
                remaining_time = max(1, int(avg_closure_time - (current_time - closure_start).total_seconds() / 60))
                if remaining_time > 1:
                    display_details = f"Closed {format_time(closure_start)}, opens {format_time(estimated_open_time)} in {remaining_time}m"
                else:
                    display_details = f"Closed {format_time(closure_start)}, opening soon"
            else:
                display_details = f"Closed {format_time(closure_start)}"
            
            if action_status:
                display_details += f" ({action_status})"
    else:
        # Handle unknown or new statuses
        if "Available" in current_status:
            display_status = "OPEN NOW"
        elif "Unavailable" in current_status:
            display_status = "CLOSED NOW"
        else:
            display_status = "UNKNOWN"
        
        display_details = current_status
        if action_status:
            display_details += f" ({action_status})"

    return display_status, display_details

def fetch_bridge_status():
    global bridge_status
    try:
        logger.info("Fetching bridge status")
        response = requests.get(URL)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        bridge_tables = soup.find_all('table', {'id': 'grey_box'})
        logger.info(f"Found {len(bridge_tables)} bridge tables")
        
        last_updated = get_current_time()
        updated_status = []
        
        for idx, table in enumerate(bridge_tables, 1):
            try:
                bridge_name = table.find('span', {'class': 'lgtextblack'}).text.strip()
                status = table.find('span', {'id': 'status'}).text.strip()
                logger.info(f"Bridge {idx} name: {bridge_name}, status: {status}")
                
                current_status, action_status = parse_status(status)
                
                bridge_data = bridge_stats.get_bridge_stat(idx)
                if not bridge_data:
                    bridge_data = bridge_stats.create_new_bridge_stat(idx, bridge_name, current_status, last_updated)
                
                bridge_stats.update_bridge_stat(idx, bridge_name, current_status, action_status, last_updated)
                
                display_status, display_details = format_display_data(current_status, action_status, last_updated, bridge_data)
                
                bridge_data_entry = {
                    'id': idx,
                    'location': bridge_name,
                    'state': display_status,
                    'info': display_details
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