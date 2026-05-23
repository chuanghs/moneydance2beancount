#!/bin/bash
# export-beancount.sh

# 1. Locate the project root relative to this script
ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
VENV_PYTHON="$ROOT_DIR/.venv/bin/python"

# 2. Safety check: does the venv actually exist?
if [ ! -f "$VENV_PYTHON" ]; then
    echo "Error: Virtual environment not found at $ROOT_DIR/.venv"
    echo "Please ensure you have run your setup/install steps."
    exit 1
fi

# 3. Invoke the exporter
# We use -m to handle package imports correctly
exec "$VENV_PYTHON" -m src.beancount_exporter "$@"
