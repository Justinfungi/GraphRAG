# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container
COPY . /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5010 available to the world outside this container
EXPOSE 5010

# Set up Python path
ENV PYTHONPATH=/app/src

# Set Hugging Face token
ENV HUGGING_FACE_HUB_TOKEN=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

# Define environment variable for Flask
ENV FLASK_APP=src/web/app.py
ENV FLASK_ENV=production

# Run the application
CMD ["flask", "run", "--host=0.0.0.0", "--port=5010"]
