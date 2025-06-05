#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🚀 Starting LlamaRAG Sales Agent System..."
echo "========================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment not found.${NC}"
    echo "Please run ./scripts/setup.sh first"
    exit 1
fi

# Activate virtual environment
echo "🐍 Activating Python virtual environment..."
source venv/bin/activate

# Check if OpenAI API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    # Try to load from .env file
    if [ -f ".env" ]; then
        echo "📋 Loading environment variables from .env..."
        export $(cat .env | grep -v '^#' | xargs)
    fi
    
    if [ -z "$OPENAI_API_KEY" ]; then
        echo -e "${YELLOW}⚠️  OPENAI_API_KEY not set!${NC}"
        echo "Agent features will not work without it."
        echo "Set it with: export OPENAI_API_KEY='your-key'"
        echo "Or add it to your .env file"
        echo ""
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        echo -e "${GREEN}✅ OpenAI API key detected${NC}"
    fi
fi

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    
    # Kill backend process
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo "   ✓ Backend stopped"
    fi
    
    # Kill frontend process
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo "   ✓ Frontend stopped"
    fi
    
    # Kill any remaining processes on the ports
    lsof -ti:8000 | xargs kill -9 2>/dev/null
    lsof -ti:3000 | xargs kill -9 2>/dev/null
    
    echo "👋 Goodbye!"
    exit
}

# Set trap to cleanup on CTRL+C
trap cleanup INT TERM

# Start Backend
echo ""
echo "🔧 Starting Backend API Server..."
echo "--------------------------------"
python main.py &
BACKEND_PID=$!

# Wait for backend to start
echo "⏳ Waiting for backend to initialize..."
sleep 5

# Check if backend is running
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${RED}❌ Backend failed to start${NC}"
    echo "Check the logs above for errors"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo -e "${GREEN}✅ Backend is running on http://localhost:8000${NC}"

# Check if frontend directory exists
if [ ! -d "frontend" ]; then
    echo -e "${YELLOW}⚠️  Frontend directory not found${NC}"
    echo "Chat UI will not be available"
    echo "API is still accessible at http://localhost:8000"
    echo ""
    echo "Press CTRL+C to stop the backend"
    wait $BACKEND_PID
    exit 0
fi

# Check if node_modules exists
if [ ! -d "frontend/node_modules" ]; then
    echo -e "${YELLOW}⚠️  Frontend dependencies not installed${NC}"
    echo "Installing now..."
    cd frontend
    npm install --legacy-peer-deps
    cd ..
fi

# Start Frontend
echo ""
echo "🎨 Starting Frontend UI Server..."
echo "--------------------------------"
cd frontend
npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
echo "⏳ Waiting for frontend to initialize..."
sleep 8

# Check if frontend is running
if ! curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Frontend may not have started properly${NC}"
    echo "Check logs at /tmp/frontend.log"
else
    echo -e "${GREEN}✅ Frontend is running on http://localhost:3000${NC}"
fi

echo ""
echo "========================================"
echo -e "${GREEN}✅ All services are running!${NC}"
echo ""
echo "🌐 Access points:"
echo "   - Chat UI:    http://localhost:3000"
echo "   - Upload UI:  http://localhost:8000"
echo "   - API Docs:   See docs/API_DOCS.md"
echo ""
echo "📚 Quick tips:"
echo "   - Upload documents at http://localhost:8000"
echo "   - Chat with the agent at http://localhost:3000"
echo "   - View backend logs in this terminal"
echo "   - View frontend logs: tail -f /tmp/frontend.log"
echo ""
echo -e "${YELLOW}Press CTRL+C to stop all services${NC}"
echo "========================================"

# Wait for processes
wait