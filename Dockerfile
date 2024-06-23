# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory to /app
WORKDIR /app

# Install build dependencies
RUN apt-get update && \
    apt-get install -y build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container at /app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV BRIDGE_STATUS_URL=https://seaway-greatlakes.com/bridgestatus/detailsnai?key=BridgeSCT
ENV FETCH_INTERVAL=30
ENV API_KEY=your_secret_api_key_here

# Expose port 5000
EXPOSE 5000

# Command to run the application using Waitress
CMD ["python", "start_waitress.py"]