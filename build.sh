#!/bin/bash
# Railway build script - explicitly build Python backend

set -e

echo "🐍 Installing Python dependencies..."
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt

echo "📦 Bundling frontend for deployment..."
if [ -d "frontend" ] && [ -d "backend" ]; then
  rm -rf backend/frontend
  cp -r frontend backend/frontend
  echo "✓ Copied frontend -> backend/frontend"
elif [ -d "../frontend" ] && [ ! -d "frontend" ]; then
  cp -r ../frontend frontend
  echo "✓ Copied ../frontend -> frontend"
fi

echo "✓ Build complete"
