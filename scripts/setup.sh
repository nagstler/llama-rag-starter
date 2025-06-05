#!/bin/bash

set -e  # Exit on first error
set -o pipefail

echo "🚀 Setting up LlamaIndex RAG demo..."

# Step 1: Use Python 3.10+ for compatibility
PYTHON_VERSION=$(python3 --version | awk '{print $2}' | cut -d. -f1,2)
if [[ $(echo "$PYTHON_VERSION < 3.10" | bc) -eq 1 ]]; then
  echo "❌ Python 3.10+ is required. You are using Python $PYTHON_VERSION"
  echo "👉 Please install Python 3.10+ via pyenv or system package manager"
  exit 1
fi

# Step 2: Create venv
if [ ! -d "venv" ]; then
  echo "📦 Creating virtual environment..."
  python3 -m venv venv
fi

# Step 3: Activate venv
source venv/bin/activate

# Step 4: Upgrade pip and tools
echo "🔧 Upgrading pip and tooling..."
pip install --upgrade pip setuptools wheel

# Step 5: Base requirements
echo "📚 Installing core Python dependencies..."
pip install \
  openai \
  tqdm \
  PyPDF2 \
  pypdf \
  pdfplumber \
  pypdfium2 \
  python-docx \
  flask \
  werkzeug \
  llama-index==0.12.28 \
  langchain>=0.1.0 \
  langchain-openai>=0.0.5 \
  streamlit>=1.31.0 \
  requests

# Step 6: Platform-specific handling
echo "🧠 Installing FAISS and vector store support..."

if [[ "$OSTYPE" == "darwin"* ]]; then
  echo "🍎 macOS detected"

  # Ensure libomp for Apple Clang (required for FAISS on macOS)
  if ! command -v brew >/dev/null 2>&1; then
    echo "❌ Homebrew not found. Please install Homebrew to proceed: https://brew.sh"
    exit 1
  fi

  brew install libomp || true

  # Install FAISS and vector store module
  CFLAGS="-Xpreprocessor -fopenmp -I/opt/homebrew/include" \
  LDFLAGS="-L/opt/homebrew/lib" \
  pip install faiss-cpu --no-cache-dir

else
  echo "🐧 Linux detected"
  pip install faiss-cpu
fi

# Install vector store module and file readers
pip install llama-index-vector-stores-faiss llama-index-readers-file

# Step 7: Create required directories
echo "📁 Creating data and index directories..."
mkdir -p data index

# Step 8: Create .env file if it doesn't exist
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your OpenAI API key"
fi

# Final check
echo ""
echo "🧪 Validating installations..."

# Check each critical component
FAILED=0

# Check LlamaIndex components
if python -c "from llama_index.vector_stores.faiss import FaissVectorStore" 2>/dev/null; then
    echo "✅ FaissVectorStore is working"
else
    echo "❌ FaissVectorStore failed to import"
    FAILED=1
fi

if python -c "from llama_index.readers.file import PDFReader" 2>/dev/null; then
    echo "✅ PDFReader is working"
else
    echo "❌ PDFReader failed to import"
    FAILED=1
fi

# Check LangChain
if python -c "from langchain_openai import ChatOpenAI" 2>/dev/null; then
    echo "✅ LangChain OpenAI is working"
else
    echo "❌ LangChain OpenAI failed to import"
    FAILED=1
fi

# Check Streamlit
if python -c "import streamlit" 2>/dev/null; then
    echo "✅ Streamlit is working"
else
    echo "❌ Streamlit failed to import"
    FAILED=1
fi

# Check Flask
if python -c "import flask" 2>/dev/null; then
    echo "✅ Flask is working"
else
    echo "❌ Flask failed to import"
    FAILED=1
fi

# Agent modules check (optional - will be created when running)
python -c "from agents.sales_ops import SalesOpsAgent" 2>/dev/null && echo "✅ Sales Agent modules found" || echo "ℹ️  Agent modules will be available after first run"

if [ $FAILED -eq 0 ]; then
    echo ""
    echo "✅ All critical components installed successfully!"
else
    echo ""
    echo "⚠️  Some components failed. Try running the script again or install missing components manually."
    exit 1
fi

# 👇 Friendly instructions to user
echo ""
echo "🚀 You're all set!"
echo ""
echo "👉 Next steps:"
echo "1. Configure your environment:"
echo "   export OPENAI_API_KEY='your-openai-api-key'"
echo "   # Or create .env file with OPENAI_API_KEY=your-key"
echo ""
echo "2. Run the application:"
echo "   python main.py"
echo "   # Or use: make run"
echo ""
echo "3. Open your browser:"
echo "   http://localhost:8000"
echo ""
echo "📤 Upload documents through the web interface"
echo "🔍 Query via API: curl -X POST http://localhost:8000/query -H \"Content-Type: application/json\" -d '{\"query\":\"Your question\"}'"
echo "🤖 Chat with Agent: curl -X POST http://localhost:8000/agent/chat -H \"Content-Type: application/json\" -d '{\"message\":\"What sales data do you have?\"}'"
echo ""
echo "📚 Test the agent: python test_agent.py"
echo "💬 Run chat UI: streamlit run streamlit_chat.py"
echo "📖 See docs/AGENT_USAGE.md for agent documentation"
echo "📖 See README.md for complete documentation"
echo ""
echo "🏃 Quick Start:"
echo "   Terminal 1: python main.py          # Start API server"
echo "   Terminal 2: streamlit run streamlit_chat.py  # Start chat UI"
echo "   Browser: http://localhost:8501      # Open chat interface"
