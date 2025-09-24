# Automation Control Web App

This repository contains a Flask web application designed to control a browser automation script. It provides a simple web interface to start and stop the automation, which runs in a headless Chrome browser inside a Docker container.

## Features

- **Web UI:** A single-page interface to upload credentials, specify a target, and control the automation.
- **Background Processing:** The automation runs in a background thread, allowing the web server to remain responsive.
- **Dockerized:** The entire application is containerized with Docker, including a headless Chrome browser.
- **Railway Ready:** Includes a `Dockerfile` and instructions for easy deployment on Railway.

## Local Development

### Prerequisites

- Python 3.9+
- `venv` for virtual environment management

### Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd deployment-pokemon
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    # On Windows
    .venv\Scripts\activate
    # On macOS/Linux
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Flask application:**
    ```bash
    python main.py
    ```
    The application will be available at `http://127.0.0.1:5000`.

## Docker

### Build the Image

To build the Docker image, run the following command from the root of the repository:
```bash
docker build -t automation-app .
```

### Run the Container

To run the application in a Docker container:
```bash
docker run -p 8080:8080 automation-app
```
The application will be accessible at `http://localhost:8080`.

## Deployment to Railway

This application is configured for easy deployment on Railway.

### Option 1: Deploy from GitHub

1.  **Create a new GitHub repository** and push the code to it.
2.  **Go to your Railway dashboard.**
3.  Click **New Project** and select **Deploy from GitHub repo**.
4.  Choose your repository. Railway will automatically detect the `Dockerfile` and build/deploy the application.
5.  Once deployed, a public URL will be provided.

### Option 2: Deploy with the Railway CLI

1.  **Install the Railway CLI.**
2.  **Log in to your Railway account:**
    ```bash
    railway login
    ```
3.  **Initialize the project:**
    ```bash
    railway init
    ```
4.  **Deploy the application:**
    ```bash
    railway up
    ```
    This command will upload your code, build the Docker image, and deploy it.

### Important Notes for Railway

-   **Ephemeral Storage:** Railway's default file system is ephemeral. Any files uploaded (like `credentials.json`) will be lost on restart or redeployment. For persistent storage, you would need to attach a Railway Volume to your service.
-   **Port:** The `Dockerfile` exposes port `8080`, and `gunicorn` is configured to bind to this port. Railway automatically detects and routes traffic to the exposed port.
