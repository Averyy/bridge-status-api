# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variables
ENV BRIDGE_STATUS_URL=https://seaway-greatlakes.com/bridgestatus/detailsnai?key=BridgeSCT
ENV FETCH_INTERVAL=30
ENV API_KEY=your_secret_api_key_here

# Run app.py when the container launches
CMD ["python", "app.py"]