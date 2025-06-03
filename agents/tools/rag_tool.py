"""RAG Query Tool - Interfaces with existing LlamaIndex RAG system."""

import os
import requests
from typing import Optional
from agents.base import BaseTool


class RAGQueryTool(BaseTool):
    """Tool to query the LlamaIndex RAG system."""
    
    def __init__(self, rag_api_url: Optional[str] = None):
        """
        Initialize RAG Query Tool.
        
        Args:
            rag_api_url: URL of the RAG API endpoint. 
                        Defaults to environment variable or http://localhost:8000
        """
        self.rag_api_url = rag_api_url or os.getenv("RAG_API_URL", "http://localhost:8000")
        
        super().__init__(
            name="rag_query",
            description=(
                "Query internal documents using the RAG system. "
                "Use this tool to search for information in indexed documents "
                "about sales data, customer information, deals, and other business data."
            )
        )
    
    def run(self, query: str) -> str:
        """
        Execute RAG query.
        
        Args:
            query: The search query
            
        Returns:
            The response from the RAG system or error message
        """
        try:
            # Make request to RAG API
            response = requests.post(
                f"{self.rag_api_url}/query",
                json={"query": query},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                # Extract the response text
                return data.get("response", "No response from RAG system")
            else:
                return f"RAG query failed with status {response.status_code}: {response.text}"
                
        except requests.exceptions.ConnectionError:
            return (
                "Failed to connect to RAG system. "
                "Please ensure the RAG API is running at " + self.rag_api_url
            )
        except requests.exceptions.Timeout:
            return "RAG query timed out. Please try again."
        except Exception as e:
            return f"Error querying RAG system: {str(e)}"