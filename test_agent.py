#!/usr/bin/env python3
"""Test script for the Sales Operations Agent"""

import requests
import json
import sys
import time

# Configuration
API_BASE_URL = "http://localhost:8000"

def test_rag_query():
    """Test direct RAG query"""
    print("\n=== Testing Direct RAG Query ===")
    response = requests.post(
        f"{API_BASE_URL}/query",
        json={"query": "What documents are in the system?"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_agent_chat(message):
    """Test agent chat"""
    print(f"\n=== Testing Agent Chat ===")
    print(f"Message: {message}")
    
    response = requests.post(
        f"{API_BASE_URL}/agent/chat",
        json={"message": message}
    )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    
    if response.status_code == 200:
        print(f"Agent: {data.get('agent', 'Unknown')}")
        print(f"Response: {data.get('response', 'No response')}")
    else:
        print(f"Error: {data}")
    
    return response.status_code == 200

def test_agent_sales_queries():
    """Test various sales-related queries"""
    queries = [
        "What sales data do you have access to?",
        "Show me information about recent deals",
        "What can you tell me about our customers?",
        "Analyze the sales performance based on available data",
        "What types of documents are indexed in the system?"
    ]
    
    for query in queries:
        print("\n" + "="*60)
        if not test_agent_chat(query):
            print("❌ Query failed!")
        time.sleep(1)  # Small delay between requests

def main():
    """Main test function"""
    print("🧪 Testing LangChain Agent Integration with RAG System")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code != 200:
            print("❌ Server is not healthy!")
            sys.exit(1)
        print("✅ Server is running")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Please ensure the RAG API is running on port 8000")
        print("   Run: python main.py")
        sys.exit(1)
    
    # Check index status
    response = requests.get(f"{API_BASE_URL}/index/status")
    status = response.json()
    print(f"\n📊 Index Status:")
    print(f"   - Index exists: {status.get('index_exists', False)}")
    print(f"   - Files indexed: {status.get('files_in_data_directory', 0)}")
    
    if not status.get('index_exists'):
        print("\n⚠️  No index found. Please upload and index some documents first!")
        print("   Use the web UI at http://localhost:8000 to upload files")
        return
    
    # Test direct RAG query
    if not test_rag_query():
        print("❌ Direct RAG query failed!")
        return
    
    # Test agent with sales queries
    print("\n🤖 Testing Sales Operations Agent...")
    test_agent_sales_queries()
    
    print("\n\n✅ Testing complete!")
    print("\nNOTE: The agent uses the RAG system to search for information.")
    print("If you see limited responses, it means you need to upload more documents.")
    print("The agent will explain when it cannot find specific information.")

if __name__ == "__main__":
    main()