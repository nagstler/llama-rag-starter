#!/bin/bash

echo "🔧 Setting up your RAG environment..."

# 1. Create virtual environment
echo "🐍 Creating virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

# 2. Upgrade pip
pip install --upgrade pip

# 3. Install all required packages
echo "📦 Installing dependencies..."
pip install llama-index \
            llama-index-vector-stores-faiss \
            llama-index-llms-openai \
            llama-index-readers-file \
            faiss-cpu \
            openai \
            PyPDF2 \
            python-docx \
            tqdm

# 4. Create required folders if not exist
mkdir -p data
mkdir -p index

# 5. Check if OPENAI_API_KEY is set
if [[ -z "${OPENAI_API_KEY}" ]]; then
  echo "⚠️  OPENAI_API_KEY not set in environment."
  echo "👉 Please export your key using:"
  echo "   export OPENAI_API_KEY=sk-..."
else
  echo "✅ OPENAI_API_KEY is set."
fi

# 6. Done
echo "🎉 Setup complete!"
echo "👉 Drop files into the ./data folder and run:"
echo "   python3 app.py"
