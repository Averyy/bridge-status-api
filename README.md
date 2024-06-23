# 🔼🚢⬇️ St. Catharines / Thorold Bridge Status API

[![Docker Image](https://img.shields.io/docker/v/averyyyy/bridge-status-api?style=flat-square&logo=docker)](https://hub.docker.com/r/averyyyy/bridge-status-api)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A simple API that scrapes the Great Lakes St. Lawrence Seaway bridge status website and provides that information for consumption. This self-hosted solution is built using Flask, BeautifulSoup, and APScheduler, and is containerized using Docker for ease of deployment.

## Table of Contents

-   [Features](#features)
-   [Prerequisites](#prerequisites)
-   [Setup](#setup)
-   [Docker Setup](#docker-setup)
-   [API Endpoints](#api-endpoints)
-   [Configuration](#configuration)
-   [Contributing](#contributing)
-   [Testing](#testing)
-   [Troubleshooting](#troubleshooting)
-   [License](#license)

## Features

-   Scrapes bridge status information from a public website
-   Provides a REST API endpoint to retrieve the bridge status
-   Secured with an API key
-   Health check endpoint

## Prerequisites

-   Docker
-   Python 3.9+
-   pip

## Setup

### 1. Clone the repository

```sh
git clone https://github.com/yourusername/bridge-status-api.git
cd bridge-status-api
```

### 2. Create a virtual environment and activate it

```sh
python -m venv venv
source venv/bin/activate # On Windows, use `venv\Scripts\activate`
```

### 3. Install dependencies

```sh
pip install -r requirements.txt
```

### 4. Set environment variables (optional)

Create a `.env` file in the project root and add the below. Note these are preset but I highly recommend changing the API_KEY to something different. It's only been tested with the St Catharine's bridges and will probably need changes to work with the others:

```dotenv
BRIDGE_STATUS_URL=https://seaway-greatlakes.com/bridgestatus/detailsnai?key=BridgeSCT
FETCH_INTERVAL=30
API_KEY=your_secret_api_key_here
```

### 5. Run the application

For local/testing use:

```sh
python app.py
```

For production / in the docker use:

```sh
python start_waitress.py
```

## Docker Setup

### 1. Build the Docker image

```sh
docker build -t bridge-status-api .
```

### 2. Run the Docker container

```sh
docker run -d -p 5000:5000 --env-file .env bridge-status-api
```

## API Endpoints

### Get Bridge Status

```http
GET /bridge-status
```

Headers:

-   `X-API-Key`: Your API key

Response:

```json
{
    "bridges": [
        {
            "id": 1,
            "location": "Bridge Name",
            "current_status": "Available/Unavailable",
            "action_status": "Raising/Lowering/etc.",
            "bridge_last_updated": "2023-06-22T15:03:01.012345"
        },
        ...
    ],
    "last_updated": "2023-06-22T15:03:01.012345"
}
```

### Health Check

```http
GET /health
```

Response:

```json
{
	"status": "healthy"
}
```

## Testing

This project includes unit tests to ensure the reliability of the API.

### Running Tests

To run the tests, follow these steps:

1. Ensure you're in the project directory and your virtual environment is activated.

2. Run the tests using pytest:

```sh
pytest test_bridge_status.py
```

## License

This project is licensed under the MIT License.
