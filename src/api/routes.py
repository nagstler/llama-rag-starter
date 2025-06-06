# src/api/routes.py

from flask import request, jsonify, send_file, Response, stream_with_context
import os
import logging
from werkzeug.utils import secure_filename
from src.core.indexer import build_and_persist_index
from src.core.query import load_query_engine
from src.core.index_manager import IndexManager
from src.core.document_processor import DocumentProcessor
from config import settings
from agents.sales_ops import SalesOpsAgent
import json
import time

# Configure logging
logger = logging.getLogger(__name__)

# Configuration
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'docx'}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

# Global query engine (loaded once)
query_engine = None

# Global sales agent (loaded once)
sales_agent = None

# Global index manager
index_manager = IndexManager()
document_processor = DocumentProcessor()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_query_engine():
    """Get or initialize the query engine"""
    global query_engine
    if query_engine is None:
        try:
            query_engine = load_query_engine()
            if query_engine is not None:
                logger.info("Query engine loaded successfully")
            else:
                logger.warning("Query engine failed to load")
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
            
            # Force reload query engine
            global query_engine
            query_engine = None
            try:
                query_engine = load_query_engine()
                logger.info(f"Query engine reloaded: {query_engine is not None}")
            except Exception as e:
                logger.error(f"Failed to reload query engine: {e}")
            
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
        """Upload files and add to index incrementally"""
        try:
            if 'files' not in request.files:
                return jsonify({
                    "success": False,
                    "error": "No files provided"
                }), 400
            
            files = request.files.getlist('files')
            uploaded_files = []
            indexed_files = []
            
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
                    
                    # Process and add to index incrementally
                    from pathlib import Path
                    documents = document_processor.process_file(Path(filepath))
                    if documents:
                        result = index_manager.add_document(filepath, documents)
                        if result["success"]:
                            indexed_files.append(filename)
            
            if not uploaded_files:
                return jsonify({
                    "success": False,
                    "error": "No valid files uploaded"
                }), 400
            
            # Reload query engine to use updated index
            global query_engine
            query_engine = None
            get_query_engine()
            
            return jsonify({
                "success": True,
                "message": "Files uploaded and indexed",
                "uploaded_files": uploaded_files,
                "indexed_files": indexed_files
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
                    "error": "Query engine not initialized. Please upload and index documents first.",
                    "response": "No documents are currently indexed. Please upload documents in the Knowledge Docs section to enable search functionality."
                }), 200  # Return 200 so the agent gets a proper response
            
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
    
    @app.route('/agent/chat/stream', methods=['POST'])
    def agent_chat_stream():
        """Stream chat responses from the sales operations agent"""
        try:
            data = request.get_json()
            
            if not data or 'message' not in data:
                return jsonify({
                    "success": False,
                    "error": "No message provided"
                }), 400
            
            message = data['message']
            
            def generate():
                # Get sales agent
                agent = get_sales_agent()
                if agent is None:
                    yield f"data: {json.dumps({'type': 'error', 'content': 'Agent not initialized'})}\n\n"
                    return
                
                # Process message with agent
                try:
                    result = agent.process(message)
                    steps = result.get("steps", [])
                    response = result.get("response", "")
                    
                    # Stream reasoning steps
                    for step in steps:
                        yield f"data: {json.dumps({'type': 'reasoning', 'step': step})}\n\n"
                        time.sleep(0.5)  # Delay for visual effect
                    
                    # True streaming: send characters progressively
                    yield f"data: {json.dumps({'type': 'content_start'})}\n\n"
                    time.sleep(0.3)
                    
                    # Stream each character individually for real streaming
                    for i, char in enumerate(response):
                        event_id = f"char_{time.time()}_{i}"
                        yield f"data: {json.dumps({'type': 'content_char', 'char': char, 'id': event_id})}\n\n"
                        # Faster typing speed for better UX
                        if char == ' ':
                            time.sleep(0.01)  # Very fast for spaces
                        elif char in '.,!?':
                            time.sleep(0.05)   # Brief pause for punctuation
                        else:
                            time.sleep(0.02)  # Fast character speed
                    
                    yield f"data: {json.dumps({'type': 'content_end'})}\n\n"
                    
                    # Send completion signal
                    yield f"data: {json.dumps({'type': 'done'})}\n\n"
                    
                except Exception as e:
                    yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
            
            return Response(
                stream_with_context(generate()),
                mimetype='text/event-stream',
                headers={
                    'Cache-Control': 'no-cache',
                    'X-Accel-Buffering': 'no'
                }
            )
            
        except Exception as e:
            logger.error(f"Error in agent chat stream: {e}")
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

    @app.route('/documents', methods=['GET'])
    def list_documents():
        """List all documents in the data directory"""
        try:
            documents = []
            index_info = index_manager.get_document_info()
            
            for root, dirs, files in os.walk(settings.DATA_DIR):
                for file in files:
                    if allowed_file(file):
                        file_path = os.path.join(root, file)
                        rel_path = os.path.relpath(file_path, settings.DATA_DIR)
                        
                        # Get file stats
                        stats = os.stat(file_path)
                        
                        # Check if indexed
                        is_indexed = file_path in index_info["documents"]
                        num_chunks = 0
                        if is_indexed:
                            num_chunks = index_info["documents"][file_path]["num_chunks"]
                        
                        documents.append({
                            "id": rel_path,
                            "name": file,
                            "path": rel_path,
                            "size": stats.st_size,
                            "modified": stats.st_mtime,
                            "type": file.rsplit('.', 1)[1].lower() if '.' in file else 'unknown',
                            "indexed": is_indexed,
                            "chunks": num_chunks
                        })
            
            # Sort by modified time (newest first)
            documents.sort(key=lambda x: x['modified'], reverse=True)
            
            return jsonify({
                "success": True,
                "documents": documents,
                "total": len(documents),
                "indexed_count": sum(1 for d in documents if d["indexed"]),
                "total_vectors": index_info["total_vectors"]
            })
            
        except Exception as e:
            logger.error(f"Error listing documents: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

    @app.route('/documents/<path:doc_id>', methods=['DELETE'])
    def delete_document(doc_id):
        """Delete a document and remove from index"""
        try:
            # Construct full path
            file_path = os.path.join(settings.DATA_DIR, doc_id)
            
            # Security check - ensure path is within data directory
            if not os.path.abspath(file_path).startswith(os.path.abspath(settings.DATA_DIR)):
                return jsonify({
                    "success": False,
                    "error": "Invalid document path"
                }), 400
            
            # Check if file exists
            if not os.path.exists(file_path):
                return jsonify({
                    "success": False,
                    "error": "Document not found"
                }), 404
            
            # Remove from index first
            index_result = index_manager.remove_document(file_path)
            
            # Delete the file
            os.remove(file_path)
            
            # Reload query engine to use updated index
            global query_engine
            query_engine = None
            get_query_engine()
            
            return jsonify({
                "success": True,
                "message": "Document deleted and removed from index",
                "vectors_removed": index_result.get("vectors_removed", 0)
            })
            
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

    @app.route('/documents/reindex', methods=['POST'])
    def reindex_documents():
        """Reindex all documents"""
        try:
            from pathlib import Path
            
            # Collect all documents and process them
            documents_by_path = {}
            
            for root, dirs, files in os.walk(settings.DATA_DIR):
                for file in files:
                    if allowed_file(file):
                        file_path = os.path.join(root, file)
                        documents = document_processor.process_file(Path(file_path))
                        if documents:
                            documents_by_path[file_path] = documents
            
            if not documents_by_path:
                return jsonify({
                    "success": False,
                    "error": "No documents found to index"
                }), 400
            
            # Rebuild the entire index
            result = index_manager.rebuild_full_index(documents_by_path)
            
            if not result["success"]:
                return jsonify({
                    "success": False,
                    "error": result.get("error", "Unknown error")
                }), 500
            
            # Reload query engine
            global query_engine
            query_engine = None
            get_query_engine()
            
            return jsonify({
                "success": True,
                "message": "Documents reindexed successfully",
                "documents_indexed": result["documents_indexed"],
                "total_vectors": result["total_vectors"]
            })
            
        except Exception as e:
            logger.error(f"Error reindexing documents: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

    @app.route('/reload-query-engine', methods=['POST'])
    def reload_query_engine():
        """Force reload the query engine"""
        try:
            global query_engine
            query_engine = None
            query_engine = load_query_engine()
            
            return jsonify({
                "success": True,
                "message": "Query engine reloaded",
                "loaded": query_engine is not None
            })
            
        except Exception as e:
            logger.error(f"Error reloading query engine: {e}")
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