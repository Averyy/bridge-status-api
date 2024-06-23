# St. Catharines / Thorold Bridge Status API

This project is a simple API that scrapes Great Lakes St. Lawrence Seaway bridge status website and provides that information for consumption that you can self host. It is built using Flask, BeautifulSoup, and APScheduler, and is containerized using Docker for ease of deployment.

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

### 4. Set environment variables

Create a `.env` file in the project root and add the following:

```dotenv
BRIDGE_STATUS_URL=https://seaway-greatlakes.com/bridgestatus/detailsnai?key=BridgeSCT
FETCH_INTERVAL=30
API_KEY=your_secret_api_key_here
```

### 5. Run the application

```sh
python app.py
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
"status": "Open/Closed",
"colour": "green/red",
"last_updated": "2023-06-22T15:03:01.012345"
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

## License

This project is licensed under the MIT License.
