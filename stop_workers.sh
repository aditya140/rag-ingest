#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Stopping all workers...${NC}"

# Check if logs directory exists
if [ ! -d "logs" ]; then
    echo -e "${RED}No logs directory found. Are the workers running?${NC}"
    exit 1
fi

# Counter for stopped workers
stopped_count=0

# Stop each worker
for pid_file in logs/*.pid; do
    if [ -f "$pid_file" ]; then
        worker_type=$(basename "$pid_file" .pid)
        pid=$(cat "$pid_file")
        
        # Check if process is running
        if ps -p $pid > /dev/null 2>&1; then
            echo -e "${YELLOW}Stopping $worker_type worker (PID: $pid)...${NC}"
            kill $pid 2>/dev/null
            
            # Wait for process to stop
            for i in {1..5}; do
                if ! ps -p $pid > /dev/null 2>&1; then
                    break
                fi
                sleep 1
            done
            
            # Force kill if still running
            if ps -p $pid > /dev/null 2>&1; then
                echo -e "${RED}Force stopping $worker_type worker...${NC}"
                kill -9 $pid 2>/dev/null
            fi
            
            stopped_count=$((stopped_count + 1))
        else
            echo -e "${RED}Worker $worker_type (PID: $pid) not running${NC}"
        fi
        
        # Remove PID file
        rm "$pid_file"
    fi
done

# Clean up log files (optional)
read -p "Do you want to clean up log files? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -f logs/*.log
    echo -e "${GREEN}Log files cleaned up${NC}"
fi

if [ $stopped_count -gt 0 ]; then
    echo -e "${GREEN}Successfully stopped $stopped_count workers${NC}"
else
    echo -e "${YELLOW}No active workers found${NC}"
fi 