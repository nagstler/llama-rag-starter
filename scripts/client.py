#!/usr/bin/env python3
"""
Example client for the RAG API
"""

import requests
import json
import sys

# API base URL
import os
BASE_URL = os.environ.get('API_URL', "http://localhost:8000")

def check_health():
    """Check if API is running"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("🏥 Health Check:", response.json())
            return True
        else:
            print("❌ API returned error:", response.status_code)
            return False
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        print("❌ API is not running. Start it with: python main.py")
        return False
    except Exception as e:
        print(f"❌ Error checking health: {e}")
        return False

def get_status():
    """Get index status"""
    response = requests.get(f"{BASE_URL}/index/status")
    print("\n📊 Index Status:")
    print(json.dumps(response.json(), indent=2))

def build_index():
    """Build index from existing files"""
    print("\n🔨 Building index...")
    response = requests.post(f"{BASE_URL}/index/build")
    print(json.dumps(response.json(), indent=2))

def upload_files(file_paths):
    """Upload files and rebuild index"""
    files = []
    for path in file_paths:
        files.append(('files', open(path, 'rb')))
    
    print(f"\n📤 Uploading {len(file_paths)} files...")
    response = requests.post(f"{BASE_URL}/index/upload", files=files)
    
    # Close files
    for _, file in files:
        file.close()
    
    print(json.dumps(response.json(), indent=2))

def query(query_text):
    """Query the index"""
    print(f"\n🔍 Query: {query_text}")
    response = requests.post(
        f"{BASE_URL}/query",
        json={"query": query_text},
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n💬 Response: {result['response']}")
    else:
        print(f"\n❌ Error: {response.status_code}")
        try:
            error_data = response.json()
            if 'error' in error_data:
                print(f"   {error_data['error']}")
        except:
            pass

def interactive_mode():
    """Interactive query mode"""
    print("\n🤖 Interactive Query Mode (type 'exit' to quit)")
    
    while True:
        query_text = input("\nYour query: ").strip()
        if query_text.lower() in ['exit', 'quit']:
            break
        
        if query_text:
            query(query_text)

def main():
    """Main client function"""
    print("🦙 RAG API Client")
    
    if not check_health():
        return
    
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python api_client.py status          - Check index status")
        print("  python api_client.py build           - Build index from data folder")
        print("  python api_client.py upload <files>  - Upload files and rebuild")
        print("  python api_client.py query <text>    - Query the index")
        print("  python api_client.py interactive     - Interactive query mode")
        return
    
    command = sys.argv[1].lower()
    
    if command == "status":
        get_status()
    elif command == "build":
        build_index()
    elif command == "upload" and len(sys.argv) > 2:
        upload_files(sys.argv[2:])
    elif command == "query" and len(sys.argv) > 2:
        query(" ".join(sys.argv[2:]))
    elif command == "interactive":
        interactive_mode()
    else:
        print("❌ Invalid command")

if __name__ == "__main__":
    main()