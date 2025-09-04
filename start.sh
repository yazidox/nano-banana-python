#!/bin/bash
# Start script for production deployment

# Create output directory if it doesn't exist
mkdir -p output

# Start the API server
python src/api.py
