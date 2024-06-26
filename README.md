# 🔼🚢⬇️ St. Catharines / Thorold Bridge Status API

[![Docker Image](https://img.shields.io/docker/v/averyyyy/bridge-status-api?style=flat-square&logo=docker)](https://hub.docker.com/r/averyyyy/bridge-status-api)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A simple API that scrapes the Great Lakes St. Lawrence Seaway bridge status website and provides that information for consumption. If they update the layout of their bridge status website it will cause this to break, but as of June 2024 the new update has been coming soon for ~2 years.

This self-hosted solution is built using Flask, BeautifulSoup, and APScheduler, and is containerized using Docker for ease of deployment. You'll need to setup your own reverse proxy.

## Table of Contents

-   [Features](#features)
-   [Prerequisites](#prerequisites)
-   [Setup](#setup)
-   [Docker Setup](#docker-setup)
-   [API Endpoints](#api-endpoints)
-   [Configuration](#configuration)
-   [Contributing](#contributing)
-   [Testing](#testing)
-   [License](#license)

## Features

-   Scrapes bridge status information from the public website
-   Provides a REST API endpoint to retrieve the bridge status
-   Secured with an API key
-   Health check endpoint
-   Unit tests

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

Create a `.env` file in the project root and add the below. Note these are defaulted but I highly recommend changing the API_KEY. It's only been tested with the St Catharine's bridges and will probably need changes to work with the others:

```dotenv
BRIDGE_STATUS_URL=https://seaway-greatlakes.com/bridgestatus/detailsnai?key=BridgeSCT
FETCH_INTERVAL=30
API_KEY=your_secret_api_key_here
BRIDGE_STATS_FILE=/app/data/bridge_stats.json
```

### 5. Run the application

For local/testing use:

```sh
python app.py
```

For production (Docker uses start_waitpress.py):

```sh
python start_waitress.py
```

Then in terminal you can test it with:

```sh
curl -H "X-API-Key: your_secret_api_key_here" http://localhost:5000/bridge-status
```

## Docker Setup

You can either build the Docker image yourself below, or download it from Docker Hub by clicking [here](https://hub.docker.com/r/averyyyy/bridge-status-api). The image is updated via a Github Workflow every time a commit it made.

### 1. Build the Docker image

```sh
docker build -t bridge-status-api .
```

### 2. Run the Docker container

No persisted history (clears when Docker updates)

```sh
docker run -d -p 5000:5000 --env-file .env bridge-status-api
```

#### For (better) persistent history storage:

Docker managed history:

```sh
docker run -d -p 5000:5000 --env-file .env -v bridge_stats:/app/data bridge-status-api
```

Or custom path example:

```sh
docker run -d -p 5000:5000 --env-file .env -v /path/on/your/host:/app/data bridge-status-api
```

## API Endpoints

### Get Bridge Status

General bridge information to provide the most up to date info

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
            "info": "Opened 7:24pm",
            "location": "Lakeshore Rd",
            "state": "OPEN NOW",
            "icon": "checkmark.circle"
        },
        ...
    ],
    "last_updated": "2023-06-22T15:03:01.012345"
}
```

### Get Bridge Statistics

Stats used to display bridge details.

```http
GET /stats
```

Headers:

-   `X-API-Key`: Your API key

Response:

```json
{
    "bridge_statistics": [
        {
            "id": 1,
            "location": "Lakeshore Rd",
            "last_status": "Available",
            "avg_closure_duration": 22,
            "avg_raising_soon_to_unavailable": 30,
            "longest_closure": 43,
            "shortest_closure": 8,
            "closure_durations": {
                "1-9m": 1,
                "10-15m": 2,
                "16-20m": 0,
                "21-25m": 2,
                "26-30m": 1,
                "31m+": 1
            },
            "last_action": null,
            "last_status_change": "2024-06-26T19:12:54.633893-04:00",
            "stats_last_updated": "2024-06-26T19:32:39.165313-04:00"
        },
        ...
    ]
}
```

### Get Bridge History

History of closures and raising_soon_times used for the above calculations

```http
GET /history
```

Headers:

-   `X-API-Key`: Your API key

Response:

```json
{
    "bridge_statistics": [
    {
        "id": 1,
        "location": "Lakeshore Rd",
        "raising_soon_times": [
            {
                "end": "2024-06-25T21:14:16.679841-04:00",
                "start": "2024-06-25T20:43:16.685525-04:00"
            },
            {
                "end": "2024-06-25T23:14:46.702959-04:00",
                "start": "2024-06-25T22:45:46.679170-04:00"
            }
        ],
        "closures": [
            {
                "end": "2024-06-25T21:56:46.692680-04:00",
                "start": "2024-06-25T21:14:16.679841-04:00"
            },
            {
                "end": "2024-06-26T01:26:46.665830-04:00",
                "start": "2024-06-26T01:14:46.689335-04:00"
            }
        ]
    },
        ...
    ]
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
