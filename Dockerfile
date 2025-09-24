# Use the official Playwright Python image which includes browsers
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set environment variables for unbuffered Python output
ENV PYTHONUNBUFFERED=1

# Expose the port the app runs on for Railway
EXPOSE 8080

# Define the command to run the application with gunicorn
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:8080", "--workers", "1"]