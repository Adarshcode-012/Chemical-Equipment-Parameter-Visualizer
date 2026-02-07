import os
import sys
from waitress import serve
# Add current directory to sys.path so we can import 'backend'
# Add current directory to sys.path so we can import 'backend'
# sys.path.insert(0, os.getcwd()) 

from backend.wsgi import application
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")



if __name__ == "__main__":
    print("🚀 Starting Production Server on http://0.0.0.0:8080")
    print("Press Ctrl+C to stop.")
    serve(application, host='0.0.0.0', port=8080)
