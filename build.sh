#!/bin/bash
# Railway build script - bundle frontend only (pip handled by Nixpacks install phase)

set -e

echo "📦 Bundling frontend for deployment..."
if [ -d "frontend" ] && [ -d "backend" ]; then
  rm -rf backend/frontend
  cp -r frontend backend/frontend
  echo "✓ Copied frontend -> backend/frontend"
elif [ -d "../frontend" ] && [ ! -d "frontend" ]; then
  cp -r ../frontend frontend
  echo "✓ Copied ../frontend -> frontend"
fi

test -d backend/frontend || test -d frontend || (echo "ERROR: frontend directory missing" && exit 1)

echo "✓ Build complete"
