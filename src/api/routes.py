# src/api/routes.py

from flask import request, jsonify, send_file
import os
import logging
from werkzeug.utils import secure_filename
from src.core.indexer import build_and_persist_index
from src.core.query import load_query_engine
from config import settings
from agents.sales_ops import SalesOpsAgent

# Configure logging
logger = logging.getLogger(__name__)

# Configuration
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'docx'}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

# Global query engine (loaded once)
query_engine = None

# Global sales agent (loaded once)
sales_agent = None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_query_engine():
    """Get or initialize the query engine"""
    global query_engine
    if query_engine is None:
        try:
            query_engine = load_query_engine()
            logger.info("Query engine loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load query engine: {e}")
            return None
    return query_engine

def get_sales_agent():
    """Get or initialize the sales agent"""
    global sales_agent
    if sales_agent is None:
        try:
            # Get the RAG API URL from environment or use default
            rag_api_url = os.environ.get('RAG_API_URL', 'http://localhost:8000')
            sales_agent = SalesOpsAgent(
                rag_api_url=rag_api_url,
                model_name="gpt-3.5-turbo",  # Use gpt-3.5 for cost efficiency
                temperature=0,
                verbose=True
            )
            logger.info("Sales agent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize sales agent: {e}")
            return None
    return sales_agent

def register_routes(app):
    """Register all routes with the Flask app"""
    
    @app.route('/', methods=['GET'])
    def serve_ui():
        """Serve the upload UI"""
        ui_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates', 'index.html')
        if os.path.exists(ui_path):
            return send_file(ui_path)
        else:
            return "Upload UI not found. Please ensure index.html exists in templates directory.", 404

    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({
            "status": "healthy",
            "service": "llama-rag-api"
        })

    @app.route('/index/build', methods=['POST'])
    def build_index():
        """Build index from files in data directory"""
        try:
            # Check if data directory has files
            data_files = []
            for root, dirs, files in os.walk(settings.DATA_DIR):
                for file in files:
                    if allowed_file(file):
                        data_files.append(file)
            
            if not data_files:
                return jsonify({
                    "success": False,
                    "error": "No valid files found in data directory"
                }), 400
            
            # Build the index
            build_and_persist_index()
            
            # Reload query engine
            global query_engine
            query_engine = None
            get_query_engine()
            
            return jsonify({
                "success": True,
                "message": "Index built successfully",
                "files_processed": data_files
            })
            
        except Exception as e:
            logger.error(f"Error building index: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

    @app.route('/index/upload', methods=['POST'])
    def upload_and_index():
        """Upload files and rebuild index"""
        try:
            if 'files' not in request.files:
                return jsonify({
                    "success": False,
                    "error": "No files provided"
                }), 400
            
            files = request.files.getlist('files')
            uploaded_files = []
            
            for file in files:
                if file and allowed_file(file.filename):
                    # Check file size
                    file.seek(0, os.SEEK_END)
                    file_size = file.tell()
                    file.seek(0)
                    
                    if file_size > MAX_FILE_SIZE:
                        continue
                    
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(settings.DATA_DIR, filename)
                    file.save(filepath)
                    uploaded_files.append(filename)
            
            if not uploaded_files:
                return jsonify({
                    "success": False,
                    "error": "No valid files uploaded"
                }), 400
            
            # Build the index with new files
            build_and_persist_index()
            
            # Reload query engine
            global query_engine
            query_engine = None
            get_query_engine()
            
            return jsonify({
                "success": True,
                "message": "Files uploaded and index rebuilt",
                "uploaded_files": uploaded_files
            })
            
        except Exception as e:
            logger.error(f"Error uploading files: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

    @app.route('/query', methods=['POST'])
    def query():
        """Query the index"""
        try:
            data = request.get_json()
            
            if not data or 'query' not in data:
                return jsonify({
                    "success": False,
                    "error": "No query provided"
                }), 400
            
            query_text = data['query']
            
            # Get query engine
            engine = get_query_engine()
            if engine is None:
                return jsonify({
                    "success": False,
                    "error": "Query engine not initialized. Please build index first."
                }), 503
            
            # Execute query
            response = engine.query(query_text)
            
            # Return simple response
            return jsonify({
                "response": str(response)
            })
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

    @app.route('/agent/chat', methods=['POST'])
    def agent_chat():
        """Chat with the sales operations agent"""
        try:
            data = request.get_json()
            
            if not data or 'message' not in data:
                return jsonify({
                    "success": False,
                    "error": "No message provided"
                }), 400
            
            message = data['message']
            
            # Get sales agent
            agent = get_sales_agent()
            if agent is None:
                return jsonify({
                    "success": False,
                    "error": "Sales agent not initialized. Please check OpenAI API key."
                }), 503
            
            # Process message with agent
            result = agent.process(message)
            
            return jsonify({
                "response": result["response"],
                "steps": result.get("steps", []),
                "agent": "sales_ops"
            })
            
        except Exception as e:
            logger.error(f"Error in agent chat: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

    @app.route('/index/status', methods=['GET'])
    def index_status():
        """Get index status"""
        try:
            # Check if index exists
            index_exists = os.path.exists(os.path.join(settings.INDEX_DIR, "faiss.index"))
            
            # Count files in data directory
            data_files = []
            for root, dirs, files in os.walk(settings.DATA_DIR):
                for file in files:
                    if allowed_file(file):
                        data_files.append(file)
            
            # Check if query engine is loaded
            engine_loaded = query_engine is not None
            
            return jsonify({
                "index_exists": index_exists,
                "query_engine_loaded": engine_loaded,
                "files_in_data_directory": len(data_files),
                "files": data_files
            })
            
        except Exception as e:
            logger.error(f"Error checking status: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

    @app.errorhandler(413)
    def request_entity_too_large(error):
        return jsonify({
            "success": False,
            "error": "File too large. Maximum size is 100MB"
        }), 413