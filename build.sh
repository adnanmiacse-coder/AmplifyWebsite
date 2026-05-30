#!/bin/bash
# Railway build script - explicitly build Python backend

set -e

echo "🐍 Installing Python dependencies..."
pip install --upgrade pip
pip install -r backend/requirements.txt

echo "✓ Build complete"
