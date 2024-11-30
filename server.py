from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

app = FastAPI()

# Configuration
SAVE_DIR = "Logs"  # Directory to store logs
MAX_SIZE = 10 * 1024 * 1024  # 10MB per log file

# Ensure the Logs directory exists
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# Pydantic model for incoming log data
class LogData(BaseModel):
    logs: str
    user_name: str  # User name (or target name)

@app.post("/logs")
async def receive_logs(data: LogData):
    logs = data.logs
    user_name = data.user_name

    if not logs.strip():
        raise HTTPException(status_code=400, detail="No logs received")

    # User-specific log file
    user_file = os.path.join(SAVE_DIR, f"{user_name}.txt")

    # Create file if it doesn't exist
    if not os.path.exists(user_file):
        try:
            with open(user_file, "w") as f:
                f.write("")  # Create an empty file
        except Exception as e:
            raise HTTPException(status_code=500, detail="Error creating user file")

    # Append received logs to the user-specific log file
    try:
        with open(user_file, "a") as f:
            f.write(logs + "\n")
        return {"status": "success", "message": f"Logs appended for user {user_name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error appending logs: {e}")

@app.get("/logs")
async def get_logs(user_name: str = None):
    if user_name:
        # Fetch logs for a specific user
        user_file = os.path.join(SAVE_DIR, f"{user_name}.txt")
        if not os.path.exists(user_file):
            raise HTTPException(status_code=404, detail=f"User log file {user_name} not found")

        try:
            with open(user_file, "r") as f:
                logs = f.readlines()
            return {"user_name": user_name, "logs": logs}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error reading log file: {e}")
    else:
        # Fetch all logs (summary)
        try:
            users = [file.replace(".txt", "") for file in os.listdir(SAVE_DIR) if file.endswith(".txt")]
            all_logs = {}
            for user in users:
                with open(os.path.join(SAVE_DIR, f"{user}.txt"), "r") as f:
                    all_logs[user] = f.readlines()
            return {"all_logs": all_logs}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching logs: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=5000)
