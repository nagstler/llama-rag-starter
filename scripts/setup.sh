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
  llama-index==0.12.28

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

# Final check
echo "✅ Setup complete."
echo "🧪 Validating installations..."

python -c "from llama_index.vector_stores.faiss import FaissVectorStore; print('✅ FaissVectorStore is working')"
python -c "from llama_index.readers.file import PDFReader; print('✅ PDFReader is working')"

# 👇 Friendly instructions to user
echo ""
echo "🚀 You're all set!"
echo ""
echo "👉 Next steps:"
echo "1. Configure your environment:"
echo "   cp .env.example .env"
echo "   # Edit .env and add your OpenAI API key"
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
echo ""
echo "📚 For more options: make help"
echo "📖 See README.md for complete documentation"
