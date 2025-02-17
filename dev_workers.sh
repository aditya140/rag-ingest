#!/bin/bash

# Create a directory for logs if it doesn't exist
mkdir -p logs

# Function to start a worker
start_worker() {
    worker_type=$1
    echo "Starting $worker_type worker..."
    python -m app.runners.${worker_type}_worker > logs/${worker_type}.log 2>&1 &
    echo $! > logs/${worker_type}.pid
    echo "$worker_type worker started with PID $(cat logs/${worker_type}.pid)"
}

# Function to stop workers
stop_workers() {
    echo "Stopping all workers..."
    for pid_file in logs/*.pid; do
        if [ -f "$pid_file" ]; then
            pid=$(cat "$pid_file")
            worker_type=$(basename "$pid_file" .pid)
            echo "Stopping $worker_type worker (PID: $pid)..."
            kill $pid 2>/dev/null || true
            rm "$pid_file"
        fi
    done
    echo "All workers stopped"
}

# Handle script termination
trap stop_workers EXIT

# Ensure PYTHONPATH includes the app directory
export PYTHONPATH=$PYTHONPATH:$(pwd)

echo "Starting development workers..."

# Start each worker type
start_worker "workflow"
start_worker "thumbnail"
start_worker "parsing"
start_worker "chunking"
start_worker "embedding"

echo "All workers started. Logs are being written to the logs directory."
echo "Press Ctrl+C to stop all workers."

# Wait for Ctrl+C
wait 