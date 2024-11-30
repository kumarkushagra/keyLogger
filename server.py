from fastapi import FastAPI, File, UploadFile, HTTPException
import os

app = FastAPI()

# Configuration
SAVE_DIR = "Logs"  # Directory to store logs
MAX_SIZE = 10 * 1024 * 1024  # 10MB per log file

# Ensure the Logs directory exists
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)


@app.post("/logs")
async def upload_log(file: UploadFile = File(...)):
    try:
        # Get target name from file
        target_name = file.filename
        
        if not target_name:
            raise HTTPException(status_code=400, detail="Invalid file name")
        
        # Determine target file path
        target_file_path = os.path.join(SAVE_DIR, target_name)
        
        # Read uploaded file data
        data = await file.read()

        if len(data) == 0:
            raise HTTPException(status_code=400, detail="Empty file uploaded")

        # Check if the file already exists
        if os.path.exists(target_file_path):
            # Check if size exceeds limit
            if os.path.getsize(target_file_path) > MAX_SIZE:
                raise HTTPException(status_code=400, detail="Target file size exceeded")
            
            # Append data to the existing file
            with open(target_file_path, "ab") as f:
                f.write(data)
            return {"status": "success", "message": f"Appended data to {target_name}"}
        else:
            # Create a new target file and write data
            with open(target_file_path, "wb") as f:
                f.write(data)
            return {"status": "success", "message": f"Created new target {target_name} and added data"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=5000)  # Port set to 5000
