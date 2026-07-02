#!/bin/sh
# docker-entrypoint.sh — Inject runtime environment variables into the built React app
# This allows the Docker image to be built once and deployed to any environment
# by injecting the correct API URLs at container startup time.

set -e

# Replace placeholder API URL in built JS files
REACT_APP_API_URL="${REACT_APP_API_URL:-https://api.edusphere.school/api/v1}"
REACT_APP_WS_URL="${REACT_APP_WS_URL:-wss://api.edusphere.school}"

echo "🔧 Injecting runtime configuration..."
echo "   REACT_APP_API_URL = $REACT_APP_API_URL"
echo "   REACT_APP_WS_URL  = $REACT_APP_WS_URL"

# Find all JS files in the build and replace the placeholder
find /usr/share/nginx/html/static/js -name "*.js" -exec \
  sed -i "s|REACT_APP_API_URL_PLACEHOLDER|${REACT_APP_API_URL}|g" {} \;

find /usr/share/nginx/html/static/js -name "*.js" -exec \
  sed -i "s|REACT_APP_WS_URL_PLACEHOLDER|${REACT_APP_WS_URL}|g" {} \;

echo "✅ Configuration injected. Starting Nginx..."

# Execute the CMD (nginx -g daemon off;)
exec "$@"
