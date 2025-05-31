# Makefile for llama-rag-starter

# Variables
PYTHON := python3
VENV := venv
PORT := 8000

# Default target
.DEFAULT_GOAL := help

# Help target
.PHONY: help
help:
	@echo "Available targets:"
	@echo "  make install     - Install dependencies"
	@echo "  make setup       - Run complete setup (create venv, install deps)"
	@echo "  make run         - Run the API server"
	@echo "  make build-index - Build index from data directory"
	@echo "  make clean       - Clean up generated files"
	@echo "  make test        - Run tests"
	@echo "  make lint        - Run linting"
	@echo "  make format      - Format code"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-run   - Run Docker container"

# Setup virtual environment and install dependencies
.PHONY: setup
setup:
	@echo "🔧 Setting up virtual environment..."
	$(PYTHON) -m venv $(VENV)
	@echo "📦 Installing dependencies..."
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -r requirements.txt
	@echo "✅ Setup complete! Activate with: source $(VENV)/bin/activate"

# Install dependencies (assumes venv is activated)
.PHONY: install
install:
	pip install --upgrade pip
	pip install -r requirements.txt

# Run the API server
.PHONY: run
run:
	@echo "🚀 Starting RAG API on port $(PORT)..."
	$(PYTHON) main.py

# Build index from data directory
.PHONY: build-index
build-index:
	@echo "📚 Building index from data directory..."
	$(PYTHON) -m src.core.indexer

# Clean up generated files
.PHONY: clean
clean:
	@echo "🧹 Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".DS_Store" -delete
	@echo "✅ Cleanup complete"

# Run tests
.PHONY: test
test:
	@echo "🧪 Running tests..."
	$(PYTHON) -m pytest tests/ -v

# Run linting
.PHONY: lint
lint:
	@echo "🔍 Running linting..."
	$(PYTHON) -m flake8 src/ --max-line-length=100
	$(PYTHON) -m pylint src/

# Format code
.PHONY: format
format:
	@echo "✨ Formatting code..."
	$(PYTHON) -m black src/ tests/
	$(PYTHON) -m isort src/ tests/

# Docker targets
.PHONY: docker-build
docker-build:
	@echo "🐳 Building Docker image..."
	docker build -t llama-rag-starter .

.PHONY: docker-run
docker-run:
	@echo "🐳 Running Docker container..."
	docker run -p $(PORT):$(PORT) -v ./data:/app/data llama-rag-starter

# Development server with auto-reload
.PHONY: dev
dev:
	@echo "🔄 Starting development server with auto-reload..."
	FLASK_ENV=development $(PYTHON) main.py