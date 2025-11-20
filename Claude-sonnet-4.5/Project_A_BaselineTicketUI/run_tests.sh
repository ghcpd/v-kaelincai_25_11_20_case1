#!/bin/bash
# Run tests for Project A - Baseline Ticket UI

echo "=========================================="
echo "Running Tests - Baseline Ticket UI"
echo "=========================================="
echo ""

# Activate virtual environment if exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Run tests
echo "Executing test runner..."
python tests/test_runner.py

echo ""
echo "=========================================="
echo "Test execution complete!"
echo "Results saved to: results/"
echo "=========================================="
