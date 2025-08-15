#!/bin/sh

# Exit immediately if a command exits with a non-zero status.
set -e

# The 'exec' command replaces the shell with the given program.
# We use a case statement to run the correct command based on the
# STARTUP_COMMAND environment variable provided in render.yaml.

case "$STARTUP_COMMAND" in
  api)
    echo "Starting API server..."
    exec gunicorn backend.api:app
    ;;
  frontend)
    echo "Starting Streamlit frontend..."
    exec python -m streamlit run app.py --server.port=8501 --server.address=0.0.0.0
    ;;
  scheduler)
    echo "Starting scheduler..."
    exec python scripts/scheduled_tasks.py
    ;;
  *)
    echo "Unknown STARTUP_COMMAND: $STARTUP_COMMAND"
    exit 1
    ;;
esac