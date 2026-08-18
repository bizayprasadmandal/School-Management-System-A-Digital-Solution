#!/bin/sh
# docker-entrypoint.sh — Inject runtime environment variables into the built Vite app
# This allows the Docker image to be built once and deployed to any environment
# by injecting the correct API URLs at container startup time.

set -e

# Replace placeholder API URL in built JS files
VITE_API_URL="${VITE_API_URL:-https://api.edusphere.school/api/v1}"
VITE_WS_URL="${VITE_WS_URL:-wss://api.edusphere.school}"

echo "🔧 Injecting runtime configuration..."
echo "   VITE_API_URL = $VITE_API_URL"
echo "   VITE_WS_URL  = $VITE_WS_URL"

# Find all JS files in the build and replace the placeholder
find /usr/share/nginx/html/assets -name "*.js" -exec \
  sed -i "s|VITE_API_URL_PLACEHOLDER|${VITE_API_URL}|g" {} \;

find /usr/share/nginx/html/assets -name "*.js" -exec \
  sed -i "s|VITE_WS_URL_PLACEHOLDER|${VITE_WS_URL}|g" {} \;

echo "✅ Configuration injected. Starting Nginx..."

# Execute the CMD (nginx -g daemon off;)
exec "$@"
