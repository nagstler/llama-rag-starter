#!/usr/bin/env python3
"""
Migrate existing FAISS index to work with the new IndexManager system.
This script ensures backward compatibility with existing indexes.
"""

import os
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings
from src.core.index_manager import IndexManager
from src.core.document_processor import DocumentProcessor

def migrate_existing_index():
    """Migrate existing index to new format with document mapping"""
    
    index_manager = IndexManager()
    document_processor = DocumentProcessor()
    
    # Check if we already have a mapping file
    if os.path.exists(index_manager.mapping_file):
        with open(index_manager.mapping_file, 'r') as f:
            mapping = json.load(f)
            if mapping.get("documents"):
                print("✅ Index already migrated!")
                return
    
    print("🔄 Migrating existing index to new format...")
    
    # Get all documents in data directory
    documents_to_index = {}
    data_dir = Path(settings.DATA_DIR)
    
    for file_path in data_dir.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in {'.pdf', '.txt', '.docx'}:
            print(f"  Processing: {file_path.name}")
            docs = document_processor.process_file(file_path)
            if docs:
                documents_to_index[str(file_path)] = docs
    
    if not documents_to_index:
        print("❌ No documents found to migrate")
        return
    
    # Rebuild index with proper tracking
    print(f"\n📚 Rebuilding index for {len(documents_to_index)} documents...")
    result = index_manager.rebuild_full_index(documents_to_index)
    
    if result["success"]:
        print(f"✅ Migration complete!")
        print(f"   - Documents indexed: {result['documents_indexed']}")
        print(f"   - Total vectors: {result['total_vectors']}")
    else:
        print(f"❌ Migration failed: {result.get('error')}")

if __name__ == "__main__":
    migrate_existing_index()