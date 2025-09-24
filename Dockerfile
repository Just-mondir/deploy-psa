# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies including Chromium
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    --no-install-recommends

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code
COPY . .

# Expose the port the app runs on
EXPOSE 8080

# Define the command to run the application
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:8080", "--workers", "1"]
