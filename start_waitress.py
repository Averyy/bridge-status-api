# start_waitress.py
from scheduler_init import start_scheduler
import waitress
from app import app

if __name__ == "__main__":
    start_scheduler()
    waitress.serve(app, listen="0.0.0.0:5000")