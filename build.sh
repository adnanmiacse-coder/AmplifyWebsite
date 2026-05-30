#!/bin/bash
# Railway build script - explicitly build Python backend

set -e

echo "🐍 Installing Python dependencies..."
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt

echo "✓ Build complete"
