# Next.js Chat UI Documentation

## Overview

This document explains the production-ready Next.js chat interface that replaced Streamlit. The new UI provides real-time streaming, professional styling, and better performance.

## Migration from Streamlit

### Why We Migrated

| Aspect | Streamlit | Next.js |
|--------|-----------|---------|
| **Performance** | Full page reruns | Efficient React updates |
| **Streaming** | Simulated only | Real SSE streaming |
| **Production Ready** | Development tool | Production framework |
| **Customization** | Limited | Full control |
| **Scalability** | Single server | Can be distributed |

### What Changed

1. **Removed**:
   - `streamlit_chat.py`
   - Streamlit dependencies
   - `run_all.sh` script

2. **Added**:
   - `frontend/` directory with Next.js app
   - SSE streaming endpoint in Flask
   - Production-ready chat UI

## Architecture

```
Browser (Next.js) ←→ Next.js Server ←→ Flask API ←→ LangChain Agent
    ↓                     ↓                ↓              ↓
React UI            API Proxy       SSE Stream      Tool Calls
```

## Implementation Details

### 1. Server-Side Events (SSE)

The Flask backend now supports streaming:

```python
@app.route('/agent/chat/stream', methods=['POST'])
def agent_chat_stream():
    def generate():
        # Stream reasoning steps
        for step in steps:
            yield f"data: {json.dumps({'type': 'reasoning', 'step': step})}\n\n"
        
        # Stream content chunks
        for chunk in chunks:
            yield f"data: {json.dumps({'type': 'content', 'content': chunk})}\n\n"
```

### 2. Frontend Streaming Consumer

```typescript
const response = await fetch('/api/agent/chat/stream', {
  method: 'POST',
  body: JSON.stringify({ message })
});

const reader = response.body?.getReader();
// Parse SSE stream and update UI in real-time
```

### 3. Message State Management

```typescript
interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  reasoning?: ReasoningStep[];
}

// React state for messages
const [messages, setMessages] = useState<Message[]>([]);
```

### 4. Reasoning Display

Agent reasoning steps are displayed inline:

```typescript
{message.reasoning?.map((step, index) => (
  <div key={index} className="flex items-start gap-2">
    <span>{getStepIcon(step.type)}</span>
    <span>{step.content}</span>
  </div>
))}
```

## Features

### 1. Real-Time Streaming
- Character-by-character response display
- No page refreshes
- Smooth animations

### 2. Agent Reasoning Visualization
- Step-by-step display
- Icon-coded step types
- Toggle visibility

### 3. Professional UI
- Clean, modern design
- Responsive layout
- Accessibility features

### 4. Example Questions
- One-click examples
- Sidebar controls
- Clear chat functionality

## Development Workflow

### 1. Start Backend
```bash
cd llama-rag-starter
python main.py
```

### 2. Start Frontend
```bash
cd frontend
npm install
npm run dev
```

### 3. Access UI
Open http://localhost:3000

## Deployment

### Backend (Flask)

1. **Production WSGI**:
```python
# wsgi.py
from src.api.app import create_app
app = create_app()

# Run with Gunicorn
# gunicorn wsgi:app
```

2. **Docker**:
```dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "wsgi:app", "--bind", "0.0.0.0:8000"]
```

### Frontend (Next.js)

1. **Vercel** (Recommended):
```bash
cd frontend
vercel
```

2. **Self-hosted**:
```bash
npm run build
npm start
```

## Production Considerations

### 1. Environment Variables
```env
# Backend
OPENAI_API_KEY=sk-...
FLASK_ENV=production

# Frontend
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

### 2. CORS Configuration
Update Flask CORS for your domain:
```python
CORS(app, origins=['https://yourdomain.com'])
```

### 3. Rate Limiting
Add rate limiting to prevent abuse:
```python
from flask_limiter import Limiter
limiter = Limiter(app, key_func=get_remote_address)

@limiter.limit("10 per minute")
@app.route('/agent/chat/stream')
```

### 4. Authentication
Add authentication middleware:
```python
@require_auth
def agent_chat_stream():
    # Your code
```

## Performance Optimizations

### 1. Response Caching
Cache common queries:
```python
from flask_caching import Cache
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@cache.memoize(timeout=300)
def get_agent_response(message):
    return agent.process(message)
```

### 2. Connection Pooling
For database connections:
```python
from sqlalchemy.pool import QueuePool
engine = create_engine(url, poolclass=QueuePool)
```

### 3. CDN for Frontend
Use CDN for static assets:
```javascript
// next.config.js
module.exports = {
  assetPrefix: 'https://cdn.yourdomain.com',
}
```

## Monitoring

### 1. Error Tracking
```javascript
// Frontend
Sentry.init({ dsn: 'your-sentry-dsn' });

// Backend
sentry_sdk.init(dsn='your-sentry-dsn')
```

### 2. Analytics
```javascript
// Frontend
import { Analytics } from '@vercel/analytics/react';
<Analytics />
```

### 3. Logging
```python
# Backend
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

## Troubleshooting

### Common Issues

1. **CORS Errors**
   - Check Flask CORS configuration
   - Ensure origins match

2. **Streaming Not Working**
   - Verify SSE mime type
   - Check proxy configuration

3. **Memory Leaks**
   - Monitor event listeners
   - Clean up streams properly

## Future Enhancements

1. **WebSocket Support**: For bidirectional communication
2. **Voice Input**: Speech-to-text integration
3. **Multi-Agent Support**: Switch between different agents
4. **File Uploads**: Direct document upload in chat
5. **Export Conversations**: Download chat history

This production-ready setup provides a solid foundation for deploying your Sales Operations Agent to real users!