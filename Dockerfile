# Use an official Python image as the base
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY server.py .
COPY index.html .

# Expose the port used by FastAPI
EXPOSE 5000

# Command to run the application
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "5000"]
