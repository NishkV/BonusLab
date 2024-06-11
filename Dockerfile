# Use the official Python image from the Docker Hub
FROM python:3.11.5-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install CMake
RUN apt-get update && \
    apt-get install -y cmake && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip and install the Python packages from requirements.txt
RUN python -m pip install --upgrade pip && \
    python -m pip install -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Add a user to run the application (optional but recommended for security)
RUN adduser --disabled-password --gecos "" --home "/nonexistent" --shell "/sbin/nologin" appuser && \
    chown -R appuser:appuser /app

# Switch to the new user
USER appuser

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "focus1:app"]
