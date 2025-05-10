#!/bin/bash

# Log file for diagnostics
LOGFILE="/var/log/eb-hooks.log"

echo "$(date -u) - Starting predeploy hook script" | tee -a $LOGFILE

# Make sure tmp directory has proper permissions
echo "Ensuring /tmp directory has correct permissions..." | tee -a $LOGFILE
mkdir -p /tmp/finetuned_model
mkdir -p /tmp/pkl_models
chmod -R 777 /tmp/finetuned_model /tmp/pkl_models

# Check if we have AWS credentials with S3 access
echo "Checking AWS S3 access..." | tee -a $LOGFILE
if [ -z "$MODEL_BUCKET" ]; then
    echo "WARNING: MODEL_BUCKET environment variable not set" | tee -a $LOGFILE
fi

# Test S3 access using AWS CLI
aws s3 ls s3://$MODEL_BUCKET --max-items 1 > /tmp/s3test.log 2>&1
if [ $? -ne 0 ]; then
    echo "WARNING: Cannot list S3 bucket $MODEL_BUCKET. Check IAM permissions." | tee -a $LOGFILE
    cat /tmp/s3test.log | tee -a $LOGFILE
else
    echo "S3 access test successful" | tee -a $LOGFILE
fi

# Fix Docker socket permissions if needed (for single container Docker environment)
if [ -S /var/run/docker.sock ]; then
    echo "Setting Docker socket permissions..." | tee -a $LOGFILE
    chmod 666 /var/run/docker.sock
fi

# Install any missing packages if needed
if ! command -v jq &> /dev/null; then
    echo "Installing jq package..." | tee -a $LOGFILE
    yum -y install jq
fi

echo "$(date -u) - Predeploy hook completed" | tee -a $LOGFILE
exit 0 