"""Sales Operations Agent implementation."""

from agents.base import BaseAgent
from agents.tools import RAGQueryTool


class SalesOpsAgent(BaseAgent):
    """Agent specialized for sales operations tasks."""
    
    def __init__(self, rag_api_url: str = None, **kwargs):
        """
        Initialize Sales Operations Agent.
        
        Args:
            rag_api_url: URL of the RAG API endpoint
            **kwargs: Additional arguments for BaseAgent
        """
        super().__init__(
            name="Sales Operations Assistant",
            description="AI assistant for sales operations, deal analysis, and customer insights",
            **kwargs
        )
        
        # Add RAG Query Tool
        rag_tool = RAGQueryTool(rag_api_url)
        self.add_tool(rag_tool)
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for sales operations agent."""
        return """You are a Sales Operations Assistant, an AI agent that helps with sales-related queries.

Your capabilities include:
- Searching internal documents for sales data, customer information, and deal details
- Analyzing sales performance and trends
- Providing insights on customers and deals
- Answering questions about sales operations

When responding to queries:
1. Use the rag_query tool to search for relevant information in the indexed documents
2. If the information is not found, explain what data might be missing
3. Provide clear, actionable insights based on the data you find
4. Be specific and include relevant details like deal amounts, customer names, and dates

Remember: You currently only have access to documents that have been indexed in the RAG system. 
If recent data is needed but not available, mention this limitation in your response."""