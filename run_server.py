#!/usr/bin/env python3
import os
import sys
import subprocess

# Change to backend directory
os.chdir('backend')

# Get port from environment or default to 8000
port = os.environ.get('PORT', '8000')

# Run uvicorn
cmd = [
    sys.executable, '-m', 'uvicorn', 
    'app.main:app',
    '--host', '0.0.0.0',
    '--port', port
]

subprocess.run(cmd)