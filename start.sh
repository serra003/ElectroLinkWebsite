#!/bin/bash
# ----------------------------------------
# Start script for ElectroLinkWebsite on Railway
# ----------------------------------------

# Step 1: Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Step 2: Start the Python backend
echo "Starting the backend..."
python backend-files/app.py
