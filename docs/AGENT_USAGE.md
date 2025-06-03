# Agent Usage Guide

## Overview

The LangChain agent is now integrated with the RAG system. The Sales Operations Agent can intelligently query your indexed documents and provide insights about sales data, customers, and deals.

## Architecture Flow

```
User Message → Agent → Decides to use RAG Tool → Queries RAG API → Returns formatted response
```

## Prerequisites

1. **Start the RAG API server**:
   ```bash
   python main.py
   ```

2. **Ensure you have documents indexed**:
   - Upload documents via the web UI at http://localhost:8000
   - Or place documents in the `data/` folder and rebuild the index

3. **Set OpenAI API key**:
   ```bash
   export OPENAI_API_KEY="your-api-key"
   ```

## API Endpoint

### Chat with Agent

**Endpoint**: `POST /agent/chat`

**Request**:
```json
{
    "message": "What deals do we have in the pipeline?"
}
```

**Response**:
```json
{
    "response": "Based on my search of the indexed documents...",
    "agent": "sales_ops"
}
```

## Example Usage

### Using cURL

```bash
# Simple query
curl -X POST http://localhost:8000/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What sales data is available?"}'

# Complex query
curl -X POST http://localhost:8000/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Analyze our customer base and identify the top segments"}'
```

### Using Python

```python
import requests

# Send message to agent
response = requests.post(
    "http://localhost:8000/agent/chat",
    json={"message": "Show me information about recent deals"}
)

print(response.json()["response"])
```

### Using the Test Script

```bash
# Run the comprehensive test
python test_agent.py
```

## Agent Capabilities

The Sales Operations Agent can:

1. **Search Documents**: Uses the RAG tool to find relevant information
2. **Analyze Data**: Interprets the found information in context
3. **Handle Missing Data**: Explains when information is not available
4. **Provide Insights**: Offers analysis based on available data

## Example Conversations

### Query 1: Basic Information
**User**: "What types of sales documents do you have?"

**Agent**: "Let me search the indexed documents for you... Based on my search, I found [specific information about available documents]"

### Query 2: Analysis Request
**User**: "Analyze our Q4 performance"

**Agent**: "I'll search for Q4 performance data... [Provides analysis based on found documents or explains if data is missing]"

### Query 3: Customer Insights
**User**: "Which customers are up for renewal?"

**Agent**: "Let me check the customer renewal information... [Searches and provides relevant customer data]"

## How It Works

1. **Agent receives message**: The agent gets your query
2. **Decides to use RAG tool**: Based on the query, it determines it needs to search documents
3. **Calls RAG API**: Uses the `rag_query` tool to search indexed documents
4. **Processes results**: Interprets the RAG response in context of your question
5. **Returns formatted answer**: Provides a helpful response

## Limitations

- The agent can only access documents that have been indexed
- If recent data is needed but not indexed, the agent will mention this
- The quality of responses depends on the quality and quantity of indexed documents

## Troubleshooting

### "Sales agent not initialized"
- Check that your `OPENAI_API_KEY` environment variable is set
- Verify the API key is valid

### "No relevant information found"
- Ensure you have uploaded and indexed documents
- Check that documents contain the information you're querying

### "Connection refused"
- Make sure the RAG API server is running on port 8000
- Check that no firewall is blocking the connection

## Next Steps

1. **Add more documents**: Upload sales reports, customer data, deal information
2. **Customize the agent**: Modify the system prompt in `agents/sales_ops/agent.py`
3. **Add more tools**: Extend the agent with additional capabilities
4. **Build a chat UI**: Create a web interface for easier interaction