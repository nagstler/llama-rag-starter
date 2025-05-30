# RAG API Documentation

This API provides endpoints for building and querying a Retrieval-Augmented Generation (RAG) system.

## Base URL
```
http://localhost:8000
```

Note: The API runs on port 8000 by default. You can change it by setting the PORT environment variable:
```bash
PORT=3000 python3 api.py
```

## Endpoints

### 1. Health Check
Check if the API is running.

**Endpoint:** `GET /health`

**Response:**
```json
{
    "status": "healthy",
    "service": "llama-rag-api"
}
```

### 2. Index Status
Get the current status of the index.

**Endpoint:** `GET /index/status`

**Response:**
```json
{
    "index_exists": true,
    "query_engine_loaded": true,
    "files_in_data_directory": 1,
    "files": ["document.pdf"]
}
```

### 3. Build Index
Build/rebuild the index from files in the data directory.

**Endpoint:** `POST /index/build`

**Response:**
```json
{
    "success": true,
    "message": "Index built successfully",
    "files_processed": ["document.pdf"]
}
```

### 4. Upload and Index
Upload files and rebuild the index.

**Endpoint:** `POST /index/upload`

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Files: Multiple files with key "files"

**Example with curl:**
```bash
curl -X POST -F "files=@document1.pdf" -F "files=@document2.pdf" http://localhost:8000/index/upload
```

**Response:**
```json
{
    "success": true,
    "message": "Files uploaded and index rebuilt",
    "uploaded_files": ["document1.pdf", "document2.pdf"]
}
```

### 5. Query
Query the RAG system.

**Endpoint:** `POST /query`

**Request:**
```json
{
    "query": "What is the speed limit in residential areas?"
}
```

**Response:**
```json
{
    "response": "The speed limit in residential areas is 25 mph, unless otherwise posted."
}
```

## Error Responses

All endpoints return error responses in this format:
```json
{
    "success": false,
    "error": "Error description"
}
```

## Status Codes
- 200: Success
- 400: Bad Request
- 413: File too large
- 500: Internal Server Error
- 503: Service Unavailable (query engine not initialized)

## File Limitations
- Maximum file size: 100MB
- Supported formats: PDF, TXT, DOCX

## Example Usage with Python

```python
import requests

# Query the index
response = requests.post(
    "http://localhost:8000/query",
    json={"query": "What are the requirements for a driver's license?"}
)
print(response.json())
```

## Example Usage with curl

```bash
# Check health
curl http://localhost:8000/health

# Get status
curl http://localhost:8000/index/status

# Build index
curl -X POST http://localhost:8000/index/build

# Query
curl -X POST -H "Content-Type: application/json" \
  -d '{"query":"What is this document about?"}' \
  http://localhost:8000/query
```