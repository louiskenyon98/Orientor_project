#!/bin/bash
cd backend
if [ -z "$PORT" ]; then
    PORT=8000
fi
python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT