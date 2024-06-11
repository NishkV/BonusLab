# Use the official Python image from the Docker Hub
FROM python:3.11.5-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install cmake, g++, and other dependencies
RUN apt-get update && \
    apt-get install -y cmake g++ && \
    rm -rf /var/lib/apt/lists/*

# Install any dependencies specified in requirements.txt
RUN python -m pip install --upgrade pip

# Install dlib from a precompiled wheel if available
RUN pip install dlib==19.24.4 --find-links https://piwheels.org/simple

# Install the remaining dependencies
RUN python -m pip install -r requirements.txt

# Copy the rest of the application code to /app
COPY . .

# Specify the command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "wsgi:app"]
