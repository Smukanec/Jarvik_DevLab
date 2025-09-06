#!/usr/bin/env bash
set -e

# Determine the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Path to the virtual environment
VENV_PATH="$SCRIPT_DIR/path/to/venv"
PID_FILE="$SCRIPT_DIR/app.pid"
LOG_FILE="$SCRIPT_DIR/app.log"

if [ ! -d "$VENV_PATH" ]; then
  echo "Virtual environment not found at $VENV_PATH" >&2
  exit 1
fi

# Activate the virtual environment
source "$VENV_PATH/bin/activate"

# Run the application in the background so it keeps running after the terminal closes
nohup python "$SCRIPT_DIR/app.py" > "$LOG_FILE" 2>&1 &
echo $! > "$PID_FILE"
echo "Application started with PID $(cat "$PID_FILE"). Logs: $LOG_FILE"
