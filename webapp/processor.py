import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pipeline import run_pipeline_main
import time

status_info = {
    "running": False,
    "progress": 0,
    "step": "",
    "done": False
}

def run_pipeline():
    status_info["running"] = True
    status_info["progress"] = 0
    status_info["done"] = False

    def update(step, progress):
        status_info["step"] = step
        status_info["progress"] = progress

    try:
        run_pipeline_main(update)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        status_info["running"] = False
        status_info["progress"] = 100
        status_info["done"] = True
