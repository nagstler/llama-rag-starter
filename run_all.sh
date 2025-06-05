#!/bin/bash
# run_all.sh - Start both the API server and Streamlit UI

echo "🚀 Starting LlamaRAG with Agent Chat UI..."
echo "=================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run ./scripts/setup.sh first"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if OpenAI API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    # Try to load from .env file
    if [ -f ".env" ]; then
        export $(cat .env | grep OPENAI_API_KEY | xargs)
    fi
    
    if [ -z "$OPENAI_API_KEY" ]; then
        echo "⚠️  OPENAI_API_KEY not set!"
        echo "Please set it with: export OPENAI_API_KEY='your-key'"
        echo "Or add it to your .env file"
    fi
fi

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    kill $API_PID $UI_PID 2>/dev/null
    exit
}

# Set trap to cleanup on CTRL+C
trap cleanup INT

# Start API server in background
echo "📡 Starting API server on port 8000..."
python main.py &
API_PID=$!

# Wait for API to start
echo "⏳ Waiting for API to be ready..."
sleep 5

# Check if API is running
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "❌ API failed to start. Check the logs above."
    kill $API_PID 2>/dev/null
    exit 1
fi

echo "✅ API is running!"

# Start Streamlit UI
echo "💬 Starting Streamlit Chat UI on port 8501..."
streamlit run streamlit_chat.py --server.headless true &
UI_PID=$!

echo ""
echo "=================================="
echo "✅ All services are running!"
echo ""
echo "🌐 Access points:"
echo "   - Chat UI: http://localhost:8501"
echo "   - Upload UI: http://localhost:8000"
echo "   - API Docs: See docs/AGENT_USAGE.md"
echo ""
echo "Press CTRL+C to stop all services"
echo "=================================="

# Wait for processes
wait