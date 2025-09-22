#!/usr/bin/env bash
# Build script for cloud deployment (Render.com, Railway, etc.)

echo "Starting build process..."

# Install Poetry if not available
if ! command -v poetry &> /dev/null; then
    echo "Installing Poetry..."
    pip install poetry
fi

# Configure Poetry for deployment
poetry config virtualenvs.create false

# Install only production dependencies
echo "Installing dependencies..."
poetry install --only=main --no-root

# Create tables if needed (will be handled by the app)
echo "Build completed successfully!"
echo "Application ready for deployment"