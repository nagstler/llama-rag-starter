# index_builder.py

import os
import faiss
import config
import logging
from pathlib import Path
from typing import List
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Document
from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.core.storage import StorageContext
from llama_index.readers.file import PDFReader

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_documents_with_fallback(data_dir: str) -> List[Document]:
    """Load documents with multiple fallback methods"""
    documents = []
    
    # Method 1: Try SimpleDirectoryReader with explicit PDF reader
    try:
        print("📂 Loading documents from:", data_dir)
        print("   Using SimpleDirectoryReader with explicit PDF reader...")
        
        # Create explicit file extractor for PDFs
        file_extractor = {".pdf": PDFReader()}
        
        reader = SimpleDirectoryReader(
            data_dir,
            recursive=True,
            file_extractor=file_extractor,
            filename_as_id=True
        )
        documents = reader.load_data()
        print(f"✅ Successfully loaded {len(documents)} documents")
        return documents
        
    except Exception as e:
        print(f"⚠️  SimpleDirectoryReader failed: {e}")
        print("   Trying fallback method...")
    
    # Method 2: Load PDFs individually
    try:
        pdf_files = list(Path(data_dir).rglob("*.pdf"))
        print(f"   Found {len(pdf_files)} PDF files")
        
        pdf_reader = PDFReader()
        for pdf_file in pdf_files:
            try:
                docs = pdf_reader.load_data(pdf_file)
                documents.extend(docs)
                print(f"   ✅ Loaded {len(docs)} pages from {pdf_file.name}")
            except Exception as e:
                print(f"   ❌ Failed to load {pdf_file.name}: {e}")
                continue
                
        if documents:
            print(f"✅ Fallback method loaded {len(documents)} documents total")
            
    except Exception as e:
        print(f"❌ All loading methods failed: {e}")
        
    return documents


def build_and_persist_index():
    try:
        # Load documents with fallback methods
        documents = load_documents_with_fallback(config.DATA_DIR)
        
        if len(documents) == 0:
            print("❌ No documents found in data directory!")
            print("   Please add PDF files to the 'data' directory")
            return
            
        # Print document info (first 5 only)
        print("\n📄 Document Summary:")
        for i, doc in enumerate(documents[:5]):
            print(f"   Document {i+1}: {doc.metadata.get('file_name', 'Unknown')}")
            print(f"   - Length: {len(doc.text)} characters")
            print(f"   - Preview: {doc.text[:100].strip()}...")
        
        if len(documents) > 5:
            print(f"   ... and {len(documents) - 5} more documents")
            
    except Exception as e:
        print(f"❌ Error loading documents: {e}")
        logger.exception("Document loading failed")
        return

    print("\n🔧 Building vector store...")
    # ✅ create and keep a reference to the faiss_index
    faiss_index = faiss.IndexFlatL2(config.EMBEDDING_DIM)
    vector_store = FaissVectorStore(faiss_index=faiss_index)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    print("📚 Creating index...")
    print(f"🔑 Using OpenAI API key: {config.OPENAI_API_KEY[:10]}...")
    
    try:
        index = VectorStoreIndex.from_documents(
            documents,
            storage_context=storage_context,
            show_progress=True
        )
        print(f"✅ Index created with {faiss_index.ntotal} vectors")
    except Exception as e:
        print(f"❌ Error creating index: {e}")
        print("💡 Make sure your OpenAI API key is valid and has credits")
        return

    print("\n💾 Saving index to:", config.INDEX_DIR)
    index.storage_context.persist(config.INDEX_DIR)

    # ✅ Save the original FAISS index reference that was actually used
    faiss_path = os.path.join(config.INDEX_DIR, "faiss.index")
    print("📦 Saving FAISS index to:", faiss_path)
    faiss.write_index(faiss_index, faiss_path)

    print(f"✅ Index built and saved with {faiss_index.ntotal} vectors")


if __name__ == "__main__":
    build_and_persist_index()
