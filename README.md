# 🧠 llama-rag-starter

> A production-ready Retrieval-Augmented Generation (RAG) starter kit using [LlamaIndex](https://www.llamaindex.ai/), [FAISS](https://github.com/facebookresearch/faiss), and [OpenAI](https://platform.openai.com/).

Build intelligent applications that can answer questions from your documents using semantic search and large language models. Features a clean web UI, REST API, and modular architecture.

---

## ✨ Features

- 🌐 **Web Upload Interface**: Drag-and-drop file upload with real-time progress
- 🔍 **Smart Document Processing**: Handles PDF, TXT, and DOCX files automatically
- 📦 **Vector Search**: Fast semantic search using FAISS and OpenAI embeddings
- 🤖 **Intelligent Responses**: GPT-3.5 generates contextual answers from your documents
- 🔌 **REST API**: Simple JSON API for programmatic access
- 🐳 **Docker Ready**: Containerized deployment with docker-compose
- 🧪 **Test Structure**: Organized for easy testing and CI/CD
- 📁 **Modular Architecture**: Clean separation of concerns for easy customization

---

## 📸 Screenshot

![Upload UI Screenshot](screenshot-placeholder.png)
*Web interface for uploading and managing documents*

---

## 🏗️ Project Structure

```
llama-rag-starter/
├── src/                      # Main source code
│   ├── api/                  # API layer
│   │   ├── app.py           # Flask application factory
│   │   └── routes.py        # API endpoints
│   ├── core/                # Core RAG functionality
│   │   ├── indexer.py       # Document indexing logic
│   │   ├── query.py         # Query engine
│   │   └── document_processor.py  # File handling
│   ├── static/              # Frontend assets (CSS, JS)
│   └── templates/           # HTML templates
│       └── index.html       # Upload UI
├── config/                  # Configuration
│   └── settings.py          # Application settings
├── scripts/                 # Utility scripts
│   ├── setup.sh            # One-click setup
│   ├── cleanup.sh          # Clean indexes
│   └── client.py           # Example API client
├── tests/                   # Test suite
├── docs/                    # Documentation
│   └── API_DOCS.md         # API reference
├── data/                    # Document storage
├── index/                   # FAISS index storage
├── main.py                  # Application entry point
├── Makefile                 # Common commands
├── requirements.txt         # Python dependencies
├── .env.example            # Environment template
├── Dockerfile              # Container configuration
└── docker-compose.yml      # Docker orchestration
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/nagstler/llama-rag-starter.git
cd llama-rag-starter

# Run automated setup
chmod +x scripts/setup.sh
./scripts/setup.sh
```

The setup script will:
- Create a Python virtual environment
- Install all dependencies
- Set up necessary directories
- Validate the installation

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-api-key-here
```

### 3. Run the Application

```bash
# Using Python directly
python main.py

# Or using Make
make run

# Or using Docker
docker-compose up
```

The application will start at `http://localhost:8000`

---

## 📖 Usage Guide

### Web Interface

1. **Open your browser** to `http://localhost:8000`
2. **Upload documents** using drag-and-drop or file browser
3. **Wait for indexing** to complete (progress shown in real-time)
4. **Query via API** using the endpoints below

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web upload interface |
| `/query` | POST | Query your documents |
| `/index/upload` | POST | Upload files via API |
| `/index/status` | GET | Check index status |
| `/index/build` | POST | Rebuild index from data folder |
| `/health` | GET | Health check |

### Query Examples

**Using cURL:**
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is this document about?"}'
```

**Using Python:**
```python
import requests

response = requests.post(
    "http://localhost:8000/query",
    json={"query": "What are the main topics covered?"}
)
print(response.json()["response"])
```

**Response Format:**
```json
{
    "response": "The document covers topics including..."
}
```

See [API_DOCS.md](docs/API_DOCS.md) for complete API documentation.

---

## 🛠️ Development

### Available Commands

```bash
make run        # Start the development server
make test       # Run test suite
make lint       # Run code linters
make format     # Format code
make clean      # Clean temporary files
make docker     # Run with Docker
make help       # Show all commands
```

### Project Configuration

Configuration is managed through environment variables and `config/settings.py`:

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `PORT`: Server port (default: 8000)
- `MAX_FILE_SIZE`: Maximum upload size (default: 100MB)
- `CHUNK_SIZE`: Document chunk size (default: 1024)
- `SIMILARITY_TOP_K`: Number of similar chunks to retrieve (default: 5)

### Adding New Features

1. **New API endpoints**: Add to `src/api/routes.py`
2. **Core functionality**: Add to `src/core/`
3. **UI changes**: Modify `src/templates/index.html`
4. **Configuration**: Update `config/settings.py`

---

## 🐳 Docker Deployment

```bash
# Build and run with docker-compose
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop containers
docker-compose down
```

---

## 🏛️ Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Browser   │────▶│  Flask API  │────▶│   LlamaIndex │
└─────────────┘     └─────────────┘     └─────────────┘
                            │                    │
                            ▼                    ▼
                    ┌─────────────┐     ┌─────────────┐
                    │    FAISS    │     │   OpenAI    │
                    │   Index     │     │     API     │
                    └─────────────┘     └─────────────┘
```

### Data Flow

1. **Upload**: Documents → Processor → Chunks → Embeddings → FAISS Index
2. **Query**: Question → Embedding → Vector Search → Context → LLM → Response

---

## 🧪 Testing

```bash
# Run all tests
make test

# Run specific test file
python -m pytest tests/test_api.py

# Run with coverage
python -m pytest --cov=src tests/
```

---

## 🚨 Troubleshooting

| Issue | Solution |
|-------|----------|
| "API key not found" | Set `OPENAI_API_KEY` in `.env` file |
| "Port already in use" | Change port: `PORT=3000 python main.py` |
| "PDF parsing error" | Ensure PDF dependencies: `pip install -r requirements.txt` |
| "No documents found" | Upload files through web UI or place in `data/` folder |
| "Import errors" | Activate virtual environment: `source venv/bin/activate` |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

## 📚 Resources

- [LlamaIndex Documentation](https://docs.llamaindex.ai/)
- [FAISS Documentation](https://github.com/facebookresearch/faiss/wiki)
- [OpenAI API Reference](https://platform.openai.com/docs)
- [Flask Documentation](https://flask.palletsprojects.com/)

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

> Built with ❤️ for AI Developers • 2025