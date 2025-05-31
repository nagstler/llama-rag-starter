# src/api/app.py

from flask import Flask
import os
import logging
from src.api.routes import register_routes, get_query_engine
from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Enable CORS for all routes
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
    
    # Register routes
    register_routes(app)
    
    return app

def run_server():
    """Run the Flask server"""
    # Create data directory if it doesn't exist
    os.makedirs(settings.DATA_DIR, exist_ok=True)
    os.makedirs(settings.INDEX_DIR, exist_ok=True)
    
    # Create app
    app = create_app()
    
    # Try to load existing index
    if os.path.exists(os.path.join(settings.INDEX_DIR, "faiss.index")):
        get_query_engine()
    
    # Run the app
    port = int(os.environ.get('PORT', 8000))
    print(f"🚀 Starting RAG API on http://localhost:{port}")
    print(f"🌐 Upload UI available at http://localhost:{port}/")
    print(f"📚 API endpoints:")
    print(f"   - POST /query - Query the index")
    print(f"   - POST /index/upload - Upload files")
    print(f"   - GET /index/status - Check status")
    print(f"📖 See API_DOCS.md for full documentation")
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == '__main__':
    run_server()