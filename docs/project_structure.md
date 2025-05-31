# Project Structure

This document describes the organization of the llama-rag-starter project.

## Directory Structure

```
llama-rag-starter/
├── src/                    # Main source code
│   ├── api/               # Flask API and routes
│   │   ├── __init__.py
│   │   ├── app.py        # Flask application factory
│   │   └── routes.py     # API route definitions
│   ├── core/             # Core RAG functionality
│   │   ├── __init__.py
│   │   ├── indexer.py    # Index building logic
│   │   ├── query.py      # Query engine logic
│   │   └── document_processor.py  # Document handling
│   ├── static/           # Static assets (CSS, JS, images)
│   └── templates/        # HTML templates
│       └── index.html    # Upload UI
├── config/               # Configuration files
│   ├── __init__.py
│   └── settings.py       # Application settings
├── scripts/              # Utility scripts
│   ├── client.py        # API client for testing
│   ├── setup.sh         # Setup script
│   └── cleanup.sh       # Cleanup script
├── tests/                # Unit tests
│   ├── __init__.py
│   └── test_api.py      # API tests
├── docs/                 # Documentation
│   └── project_structure.md
├── data/                 # Document storage (gitignored)
├── index/                # Index storage (gitignored)
├── main.py              # Main entry point
├── requirements.txt      # Python dependencies
├── Makefile             # Common commands
├── Dockerfile           # Docker configuration
├── docker-compose.yml   # Docker Compose configuration
├── .env.example         # Environment variables template
└── .gitignore           # Git ignore rules
```

## Key Components

### src/api/
- **app.py**: Flask application factory that creates and configures the app
- **routes.py**: All API endpoints and route handlers

### src/core/
- **indexer.py**: Handles building and persisting the vector index from documents
- **query.py**: Loads and manages the query engine for RAG queries
- **document_processor.py**: Processes and validates documents for indexing

### config/
- **settings.py**: Central configuration file with all app settings

### scripts/
- **client.py**: Command-line client for testing the API
- **setup.sh**: Automated setup script for the project
- **cleanup.sh**: Cleans up generated files and indices

## Running the Application

1. **Using Python directly**: `python main.py`
2. **Using Make**: `make run`
3. **Using Docker**: `docker-compose up`

## Environment Variables

See `.env.example` for required environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key
- `PORT`: Server port (default: 8000)