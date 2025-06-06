#!/bin/bash

# change running path to this script's directory
cd "$(dirname "$0")/.."

# Check if the virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Please create it first:"
    echo "uv venv"
    exit 1
fi

# Activate the virtual environment
source .venv/bin/activate

# Load environment variables from .env file if it exists
if [ -f .env ]; then
    echo "Loading environment variables from .env file..."
    export $(grep -v '^#' .env | xargs)
fi

# Check if environment variables are set
if [ -z "$DATABRICKS_HOST" ] || [ -z "$DATABRICKS_TOKEN" ]; then
    echo "Warning: DATABRICKS_HOST and/or DATABRICKS_TOKEN environment variables are not set."
    echo "You can set them now or the server will look for them in other sources."
    read -p "Do you want to continue? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Start the server by running the module directly
echo "Starting Databricks MCP server at $(date)"
if [ -n "$DATABRICKS_HOST" ]; then
    echo "Databricks Host: $DATABRICKS_HOST"
fi

python -m src.server.databricks_mcp_server --server-type sse


echo "Server stopped at $(date)" 