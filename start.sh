#!/usr/bin/env bash
set -e

# Determine the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Path to the virtual environment
VENV_PATH="$SCRIPT_DIR/path/to/venv"

if [ ! -d "$VENV_PATH" ]; then
  echo "Virtual environment not found at $VENV_PATH" >&2
  exit 1
fi

# Activate the virtual environment
source "$VENV_PATH/bin/activate"

# Run the application
exec python "$SCRIPT_DIR/app.py"
