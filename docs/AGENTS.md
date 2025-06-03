# LangChain Agents Documentation

## Overview

This project extends the existing LlamaIndex RAG system with LangChain agents to create an intelligent assistant that can:
1. Query internal documents using RAG
2. Fetch missing data from external sources (Reverse ETL)
3. Take actions based on the information gathered

## Architecture

```
User Query → LangChain Agent → Decision Making → Tool Selection → Action
                                        ↓
                                   Available Tools:
                                   1. RAG Query Tool (LlamaIndex)
                                   2. Document Sync Tool (rETL)
```

## Use Case: Sales Operations Assistant

### Scenario
A sales operations agent that can:
- Answer questions about deals, customers, and sales data
- Automatically fetch latest data from CRM when needed
- Provide insights and analysis on sales performance

### Example Flow

**User**: "What were our Q4 enterprise deals?"

**Agent Process**:
1. **Understand Intent**: Agent recognizes need for Q4 enterprise deal data
2. **Query RAG**: Calls RAG tool to search existing documents
3. **Check Data**: If data is missing or outdated, proceed to step 4
4. **Sync Data**: Calls Document Sync tool to fetch latest from CRM
5. **Re-query RAG**: Searches again with updated data
6. **Respond**: Provides comprehensive answer with sources

## Project Structure

```
llama-rag-starter/
├── agents/                    # LangChain agent implementation
│   ├── base/                 # Base classes and interfaces
│   │   └── base_agent.py     # Abstract base agent class
│   ├── tools/                # Agent tools
│   │   ├── rag_tool.py      # Tool to query LlamaIndex RAG
│   │   └── sync_tool.py     # Tool to sync external documents
│   └── sales_ops/           # Sales operations agent
│       └── agent.py         # Sales ops agent implementation
│
├── src/core/                # Existing LlamaIndex RAG (unchanged)
│   ├── indexer.py
│   ├── query.py
│   └── document_processor.py
│
└── integrations/            # External integrations
    └── slack/              # Slack integration (future)
```

## Tools

### 1. RAG Query Tool
- **Purpose**: Interface with existing LlamaIndex RAG system
- **Input**: Query string
- **Output**: Document-based answer
- **Implementation**: HTTP calls to existing `/query` endpoint

### 2. Document Sync Tool (Mock)
- **Purpose**: Simulate fetching documents from external sources
- **Input**: Source type, document type, date range
- **Output**: Status of sync operation
- **Mock Behavior**: 
  - Creates dummy sales data files
  - Places them in `data/` folder
  - Triggers re-indexing

## Implementation Details

### Base Agent Class
```python
class BaseAgent:
    """Abstract base class for all agents"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.tools = []
        self.memory = ConversationBufferMemory()
    
    def add_tool(self, tool):
        """Add a tool to the agent's toolkit"""
        pass
    
    def process(self, query: str) -> str:
        """Process a user query and return response"""
        pass
```

### Tool Interface
```python
class BaseTool:
    """Standard interface for agent tools"""
    
    name: str
    description: str  # Used by agent to decide when to use this tool
    
    def run(self, *args, **kwargs) -> str:
        """Execute the tool and return result"""
        pass
```

## Configuration

### Environment Variables
```
OPENAI_API_KEY=your-api-key      # For LangChain agents
RAG_API_URL=http://localhost:8000 # RAG system endpoint
```

### Agent Configuration
- Model: GPT-4 (configurable)
- Temperature: 0 (for consistent responses)
- Max iterations: 5 (prevent infinite loops)
- Verbose: True (for debugging)

## Development Workflow

1. **Install Dependencies**:
   ```bash
   pip install langchain langchain-openai
   ```

2. **Start RAG System**:
   ```bash
   python main.py  # Existing RAG API
   ```

3. **Test Agent**:
   ```bash
   python -m agents.sales_ops.test  # Agent testing script
   ```

## Sales Operations Examples

### Example 1: Deal Analysis
**Query**: "Show me all deals above $100k closing this quarter"
- Agent queries RAG for deal documents
- If data is stale, syncs from CRM
- Analyzes and filters deals
- Returns formatted summary

### Example 2: Customer Insights
**Query**: "Which enterprise customers haven't renewed yet?"
- Searches for renewal data in documents
- Identifies missing information
- Fetches latest customer data
- Provides actionable list

### Example 3: Performance Metrics
**Query**: "Compare this month's performance to last month"
- Retrieves current month data
- Checks for previous month data
- Syncs if necessary
- Generates comparison report

## Future Enhancements

1. **Real Integration**: Replace mock sync with actual CRM APIs
2. **More Tools**: Add email, Slack, analytics tools
3. **Agent Memory**: Persistent conversation history
4. **Multi-Agent**: Specialized agents working together
5. **UI Integration**: Chat interface in web app

## Testing Strategy

1. **Unit Tests**: Test each tool independently
2. **Integration Tests**: Test agent with mock tools
3. **End-to-End**: Test complete flows with real RAG

## Security Considerations

1. **API Keys**: Store securely, never commit
2. **Data Access**: Implement proper access controls
3. **Rate Limiting**: Prevent abuse of external APIs
4. **Audit Trail**: Log all agent actions

## Monitoring

1. **Tool Usage**: Track which tools are called
2. **Response Time**: Monitor agent performance
3. **Success Rate**: Track successful vs failed queries
4. **Cost Tracking**: Monitor LLM API usage

---

This architecture demonstrates how LangChain agents can enhance the existing LlamaIndex RAG system, creating a powerful and extensible AI assistant for business operations.