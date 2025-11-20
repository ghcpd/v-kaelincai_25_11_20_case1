#!/bin/bash
# Setup script for Project A - Baseline Ticket UI

echo "=========================================="
echo "Setting up Project A - Baseline Ticket UI"
echo "=========================================="

# Create virtual environment
echo "Creating virtual environment..."
python -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies (if any)
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "Setup complete!"
echo "To activate the environment, run: source venv/bin/activate"
