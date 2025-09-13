#!/bin/bash

# HandyConnect Startup Script

# Create necessary directories
mkdir -p data logs

# Initialize JSON data file if it doesn't exist
if [ ! -f "data/tasks.json" ]; then
    echo "Initializing JSON data storage..."
    echo "[]" > data/tasks.json
fi

# Start the application
if [ "$FLASK_ENV" = "development" ]; then
    echo "Starting HandyConnect in development mode..."
    python app.py
else
    echo "Starting HandyConnect in production mode..."
    gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app
fi
