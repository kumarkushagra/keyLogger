# Use official Python image as the base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the app will run on
EXPOSE 5000

# Command to run the app
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "5000"]
