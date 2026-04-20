#!/usr/bin/env bash
set -e

python - << 'EOF'
from main import create_app
from demo.config.settings import ApplicationSettings

app = create_app()
ApplicationSettings.load_environment(app)

print("Configuration loaded successfully")
EOF

echo "Waiting for database..."
until flask db current >/dev/null 2>&1; do
  sleep 1
done

echo "Database is ready!"

echo "Running migrations..."
flask db upgrade

echo "Starting application..."
BIND_ADDRESS="${BIND_ADDRESS:-0.0.0.0}" exec python main.py
