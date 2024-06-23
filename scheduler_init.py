from apscheduler.schedulers.background import BackgroundScheduler
from bridge_status import fetch_bridge_status
from config import FETCH_INTERVAL

scheduler = BackgroundScheduler()

def start_scheduler():
    if not scheduler.running:
        scheduler.add_job(fetch_bridge_status, 'interval', seconds=FETCH_INTERVAL, misfire_grace_time=60)
        scheduler.start()
        fetch_bridge_status()

def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()