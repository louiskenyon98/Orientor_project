# import os
# import sys
# import uvicorn

# # Add the current directory to the Python path
# current_dir = os.path.dirname(os.path.abspath(__file__))
# if current_dir not in sys.path:
#     sys.path.insert(0, current_dir)

# # This will let you run with: python run.py
# if __name__ == "__main__":
#     print("Starting server with proper Python path configuration...")
#     uvicorn.run("app.main:app", host="0.0.0.0", port=8000) #, reload=True) 

import os
import sys
import uvicorn

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # fallback to 8000 locally
    print(f"Starting server on port {port}...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)