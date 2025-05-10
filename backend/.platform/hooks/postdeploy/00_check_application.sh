#!/bin/bash

# Log file for diagnostics
LOGFILE="/var/log/eb-hooks.log"

echo "$(date -u) - Starting postdeploy hook script" | tee -a $LOGFILE

# Function to check health endpoint
check_health() {
    local attempt=1
    local max_attempts=12
    local wait_time=5
    local health_url="http://localhost:8000/health"
    
    echo "Checking application health endpoint..." | tee -a $LOGFILE
    
    while [ $attempt -le $max_attempts ]; do
        echo "Attempt $attempt of $max_attempts..." | tee -a $LOGFILE
        
        # Call health endpoint
        health_response=$(curl -s $health_url)
        health_status=$?
        
        if [ $health_status -eq 0 ]; then
            echo "Health endpoint returned: $health_response" | tee -a $LOGFILE
            
            # Check if the response contains healthy status
            if echo "$health_response" | grep -q "healthy"; then
                echo "Application is healthy!" | tee -a $LOGFILE
                return 0
            elif echo "$health_response" | grep -q "initializing"; then
                echo "Application is still initializing (loading models), waiting..." | tee -a $LOGFILE
            else
                echo "Application returned unexpected status" | tee -a $LOGFILE
            fi
        else
            echo "Health check failed, HTTP error $health_status" | tee -a $LOGFILE
        fi
        
        # Wait before next attempt
        sleep $wait_time
        attempt=$((attempt + 1))
    done
    
    echo "Health check did not succeed after $max_attempts attempts" | tee -a $LOGFILE
    return 1
}

# Check for model loading flag
check_models() {
    echo "Checking model loading status..." | tee -a $LOGFILE
    
    if [ -f "/tmp/.model_loading" ]; then
        echo "Models are still loading" | tee -a $LOGFILE
        return 1
    else
        # Check if model directories exist and have files
        if [ -d "/tmp/finetuned_model" ] && [ "$(ls -A /tmp/finetuned_model 2>/dev/null)" ]; then
            echo "SentenceTransformer model files are present" | tee -a $LOGFILE
        else
            echo "WARNING: SentenceTransformer model directory is empty or missing" | tee -a $LOGFILE
        fi
        
        if [ -d "/tmp/pkl_models" ] && [ "$(ls -A /tmp/pkl_models 2>/dev/null)" ]; then
            echo "Pickle model files are present" | tee -a $LOGFILE
        else
            echo "WARNING: Pickle model directory is empty or missing" | tee -a $LOGFILE
        fi
        
        return 0
    fi
}

# Check application logs
check_logs() {
    echo "Checking application logs for errors..." | tee -a $LOGFILE
    
    # Check Docker logs if using Docker
    if command -v docker &> /dev/null; then
        container_id=$(docker ps --filter "name=elasticbeanstalk" --format "{{.ID}}" | head -1)
        if [ ! -z "$container_id" ]; then
            echo "Found container: $container_id" | tee -a $LOGFILE
            docker logs --tail 50 $container_id 2>&1 | grep -i "error\|exception\|failed" | tee -a $LOGFILE
        fi
    fi
    
    # Also check standard EB logs
    if [ -f /var/log/eb-engine.log ]; then
        echo "Last 20 lines of EB engine log:" | tee -a $LOGFILE
        tail -20 /var/log/eb-engine.log | tee -a $LOGFILE
    fi
}

# Run all checks
check_health
check_models
check_logs

echo "$(date -u) - Postdeploy hook completed" | tee -a $LOGFILE
exit 0 