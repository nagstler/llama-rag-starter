# src/core/query.py

import os
import faiss
import logging
from llama_index.core import load_index_from_storage
from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.core.storage import StorageContext
from llama_index.llms.openai import OpenAI
from config import settings

logger = logging.getLogger(__name__)

def load_query_engine():
    """Load query engine using IndexManager"""
    try:
        from src.core.index_manager import IndexManager
        
        # Use IndexManager to get the vector store
        index_manager = IndexManager()
        
        # Check if we have any indexed documents
        doc_info = index_manager.get_document_info()
        if doc_info["total_documents"] == 0:
            logger.warning("No documents indexed. Please add documents first.")
            return None
            
        print("🔄 Loading query engine with IndexManager...")
        
        # Get the vector store from IndexManager
        faiss_index = index_manager.get_faiss_index()
        
        # Check if index is empty
        if faiss_index.ntotal == 0:
            logger.warning("FAISS index is empty. Please add documents to index.")
            return None
            
        print(f"✅ FAISS index loaded with {faiss_index.ntotal} vectors")

        # For now, use a simpler approach: rebuild the index from documents
        # This ensures everything is consistent and queryable
        print("🔄 Rebuilding query engine from indexed documents...")
        
        from pathlib import Path
        from src.core.document_processor import DocumentProcessor
        from llama_index.core import VectorStoreIndex
        from llama_index.vector_stores.faiss import FaissVectorStore
        
        # Get all documents and rebuild the index properly
        doc_processor = DocumentProcessor()
        all_documents = []
        
        # Load all documents from the mapping
        for doc_path in doc_info["documents"].keys():
            if os.path.exists(doc_path):
                documents = doc_processor.process_file(Path(doc_path))
                all_documents.extend(documents)
        
        if not all_documents:
            logger.warning("No documents could be loaded for query engine")
            return None
        
        # Create a fresh vector store and index for querying
        query_faiss_index = faiss.IndexFlatL2(settings.EMBEDDING_DIM)
        query_vector_store = FaissVectorStore(faiss_index=query_faiss_index)
        query_storage_context = StorageContext.from_defaults(vector_store=query_vector_store)
        
        # Build the index with all documents
        index = VectorStoreIndex.from_documents(
            all_documents,
            storage_context=query_storage_context,
            show_progress=True
        )
        
        query_engine = index.as_query_engine(
            llm=OpenAI(model=settings.LLM_MODEL),
            similarity_top_k=5,
            response_mode="tree_summarize",
            verbose=True
        )
        print("✅ Query engine loaded successfully")

        return query_engine
        
    except Exception as e:
        logger.error(f"Error loading query engine: {e}")
        return None