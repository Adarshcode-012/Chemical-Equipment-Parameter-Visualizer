#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install Python dependencies
pip install -r requirements.txt

# Build React App
cd web
npm install
npm run build
cd ..

# Collect Static Files (Django + React build)
python backend/manage.py collectstatic --no-input

# Run Migrations
python backend/manage.py migrate

# Create Superuser (optional, hardcoded for demo convenience)
python backend/create_superuser.py
