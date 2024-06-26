# bridge_stats.py

import json
import os
from datetime import datetime, timedelta
from config import BRIDGE_STATS_FILE

class BridgeStats:
    def __init__(self, filename=BRIDGE_STATS_FILE):
        self.filename = filename
        self.stats = self.load_stats()

    def load_stats(self):
        try:
            with open(self.filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"bridge_statistics": []}

    def save_stats(self):
        directory = os.path.dirname(self.filename)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(self.filename, 'w') as f:
            json.dump(self.stats, f, indent=2)

    def get_bridge_stat(self, bridge_id):
        return next((s for s in self.stats["bridge_statistics"] if s["id"] == bridge_id), None)

    def create_new_bridge_stat(self, bridge_id, bridge_name, status, timestamp):
        return {
            "id": bridge_id,
            "location": bridge_name,
            "last_status": status,
            "last_action": None,
            "shortest_closure": 0,
            "longest_closure": 0,
            "avg_closure_duration": 0,
            "avg_raising_soon_to_unavailable": 0,
            "closure_durations": {"1-9m": 0, "10-15m": 0, "16-20m": 0, "21-25m": 0, "26-30m": 0, "31m+": 0},
            "closures": [],
            "raising_soon_times": [],
            "last_status_change": timestamp.isoformat(),
            "stats_last_updated": timestamp.isoformat()
        }

    def update_bridge_stat(self, bridge_id, bridge_name, status, action, timestamp):
        bridge_stat = self.get_bridge_stat(bridge_id)
        if not bridge_stat:
            bridge_stat = self.create_new_bridge_stat(bridge_id, bridge_name, status, timestamp)
            self.stats["bridge_statistics"].append(bridge_stat)
        
        self.update_status(bridge_stat, status, action, timestamp)
        self.cleanup_old_data(bridge_stat, timestamp)
        
        bridge_stat["stats_last_updated"] = timestamp.isoformat()
        self.save_stats()

    def update_status(self, bridge_stat, status, action, timestamp):
        # Close out any open raising_soon periods
        if bridge_stat["raising_soon_times"] and "end" not in bridge_stat["raising_soon_times"][-1]:
            if action != "Raising Soon":
                bridge_stat["raising_soon_times"][-1]["end"] = timestamp.isoformat()
                self.update_raising_soon_stats(bridge_stat, bridge_stat["raising_soon_times"][-1])

        if status != bridge_stat["last_status"] or action != bridge_stat.get("last_action"):
            if status == "Unavailable" and bridge_stat["last_status"] == "Available":
                bridge_stat["closures"].append({"start": timestamp.isoformat()})
            elif status == "Available" and bridge_stat["last_status"] == "Unavailable":
                if bridge_stat["closures"] and "end" not in bridge_stat["closures"][-1]:
                    bridge_stat["closures"][-1]["end"] = timestamp.isoformat()
                    self.update_closure_stats(bridge_stat, bridge_stat["closures"][-1])
            
            if action == "Raising Soon":
                bridge_stat["raising_soon_times"].append({"start": timestamp.isoformat()})
            
            bridge_stat["last_status"] = status
            bridge_stat["last_action"] = action
            bridge_stat["last_status_change"] = timestamp.isoformat()

    def update_closure_stats(self, bridge_stat, closure):
        duration = round((datetime.fromisoformat(closure["end"]) - datetime.fromisoformat(closure["start"])).total_seconds() / 60)
        
        if len(bridge_stat["closures"]) == 1:
            bridge_stat["avg_closure_duration"] = duration
        else:
            total_duration = bridge_stat["avg_closure_duration"] * (len(bridge_stat["closures"]) - 1) + duration
            bridge_stat["avg_closure_duration"] = round(total_duration / len(bridge_stat["closures"]))
        
        if duration < bridge_stat["shortest_closure"] or bridge_stat["shortest_closure"] == 0:
            bridge_stat["shortest_closure"] = duration
        if duration > bridge_stat["longest_closure"]:
            bridge_stat["longest_closure"] = duration

        if duration <= 9:
            bridge_stat["closure_durations"]["1-9m"] += 1
        elif duration <= 15:
            bridge_stat["closure_durations"]["10-15m"] += 1
        elif duration <= 20:
            bridge_stat["closure_durations"]["16-20m"] += 1
        elif duration <= 25:
            bridge_stat["closure_durations"]["21-25m"] += 1
        elif duration <= 30:
            bridge_stat["closure_durations"]["26-30m"] += 1
        else:
            bridge_stat["closure_durations"]["31m+"] += 1

    def update_raising_soon_stats(self, bridge_stat, raising_soon_time):
        duration = round((datetime.fromisoformat(raising_soon_time["end"]) - datetime.fromisoformat(raising_soon_time["start"])).total_seconds() / 60)
        if len(bridge_stat["raising_soon_times"]) == 1:
            bridge_stat["avg_raising_soon_to_unavailable"] = duration
        else:
            total_duration = bridge_stat["avg_raising_soon_to_unavailable"] * (len(bridge_stat["raising_soon_times"]) - 1) + duration
            bridge_stat["avg_raising_soon_to_unavailable"] = round(total_duration / len(bridge_stat["raising_soon_times"]))

    def cleanup_old_data(self, bridge_stat, current_timestamp):
        sixty_days_ago = current_timestamp - timedelta(days=180)
        bridge_stat["closures"] = [closure for closure in bridge_stat["closures"]
                                   if datetime.fromisoformat(closure["start"]) > sixty_days_ago]
        bridge_stat["raising_soon_times"] = [time for time in bridge_stat["raising_soon_times"]
                                             if datetime.fromisoformat(time["start"]) > sixty_days_ago]
    # Output for API splitting the stats
    
    def get_filtered_stats(self):
        return [
            {k: v for k, v in stat.items() if k not in ['raising_soon_times', 'closures']}
            for stat in self.stats.get('bridge_statistics', [])
        ]
    
    def get_filtered_history(self):
        return [
            {k: v for k, v in stat.items() if k in ['raising_soon_times', 'closures', 'id', 'location']}
            for stat in self.stats.get('bridge_statistics', [])
        ]
    
bridge_stats = BridgeStats()