#!/usr/bin/env python3
import os
import subprocess
import sys

# Get port from environment, default to 8000
port = os.environ.get("PORT", "8000")

# Validate port is numeric
try:
    port_int = int(port)
    print(f"Starting server on validated port: {port_int}")
except ValueError:
    print(f"Invalid PORT value: {port}, using default 8000")
    port = "8000"

# Run uvicorn with explicit port
cmd = [
    sys.executable, "-m", "uvicorn", 
    "main:app",
    "--host", "0.0.0.0",
    "--port", str(port)
]

print(f"Executing: {' '.join(cmd)}")
subprocess.run(cmd)