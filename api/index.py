import sys
import os

# Add eta-service to sys.path so 'app' package is discoverable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "eta-service")))

from app.main import app

# Vercel serverless entrypoint
handler = app
