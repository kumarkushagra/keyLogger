from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import PlainTextResponse
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

@app.post("/logs")
async def receive_logs(data: LogData):
    logs = data.logs
    user_name = data.user_name

    if not logs.strip():
        raise HTTPException(status_code=400, detail="No logs received")

    # Create user-specific log file path
    user_file = os.path.join(SAVE_DIR, f"{user_name}.txt")

    # Read existing content (if file exists)
    old_content = ""
    if os.path.exists(user_file):
        with open(user_file, "r") as f:
            old_content = f.read()

    # Check if the log file size exceeds MAX_SIZE
    if os.path.exists(user_file) and os.path.getsize(user_file) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="User log file size exceeded")

    # Append received logs to the user-specific log file
    try:
        with open(user_file, "a") as f:
            f.write(logs + "\n")
        return {
            "status": "success",
            "file_name": f"{user_name}.txt",
            "old_content": old_content,
            "new_data": logs,
            "message": "Successfully appended"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/logs/{user_name}", response_class=PlainTextResponse)
async def get_logs(user_name: str):
    user_file = os.path.join(SAVE_DIR, f"{user_name}.txt")
    if not os.path.exists(user_file):
        raise HTTPException(status_code=404, detail="Log file not found")
    try:
        with open(user_file, "r") as f:
            content = f.read()
        return content
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error reading log file")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=5000)
