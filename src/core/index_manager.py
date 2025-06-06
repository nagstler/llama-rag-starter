# src/core/index_manager.py

import os
import json
import logging
import faiss
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from llama_index.core import VectorStoreIndex, Document
from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.core.storage import StorageContext
from config import settings

logger = logging.getLogger(__name__)

class IndexManager:
    """Manages FAISS index with document-vector mappings for scalable operations"""
    
    def __init__(self):
        self.index_dir = settings.INDEX_DIR
        # Ensure index directory exists
        os.makedirs(self.index_dir, exist_ok=True)
        
        self.mapping_file = os.path.join(self.index_dir, "document_mapping.json")
        self.faiss_index_path = os.path.join(self.index_dir, "faiss.index")
        self._mapping = self._load_mapping()
        self._faiss_index = None
        self._vector_store = None
        
    def _load_mapping(self) -> Dict:
        """Load document-vector mapping from disk"""
        if os.path.exists(self.mapping_file):
            try:
                with open(self.mapping_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading mapping: {e}")
                return {"documents": {}, "next_id": 0}
        return {"documents": {}, "next_id": 0}
    
    def _save_mapping(self):
        """Save document-vector mapping to disk"""
        os.makedirs(self.index_dir, exist_ok=True)
        with open(self.mapping_file, 'w') as f:
            json.dump(self._mapping, f, indent=2)
    
    def get_faiss_index(self) -> Optional[faiss.Index]:
        """Get or create FAISS index"""
        if self._faiss_index is None:
            if os.path.exists(self.faiss_index_path):
                self._faiss_index = faiss.read_index(self.faiss_index_path)
            else:
                # Create new index
                self._faiss_index = faiss.IndexFlatL2(settings.EMBEDDING_DIM)
        return self._faiss_index
    
    def get_vector_store(self) -> FaissVectorStore:
        """Get vector store instance"""
        if self._vector_store is None:
            faiss_index = self.get_faiss_index()
            self._vector_store = FaissVectorStore(faiss_index=faiss_index)
        return self._vector_store
    
    def add_document(self, doc_path: str, documents: List[Document]) -> Dict:
        """Add a document and its vectors to the index"""
        try:
            # Get vector store
            vector_store = self.get_vector_store()
            
            # Check if we have existing storage context
            try:
                storage_context = StorageContext.from_defaults(
                    vector_store=vector_store,
                    persist_dir=self.index_dir
                )
            except Exception:
                # If loading existing storage fails, create new one
                logger.info("Creating new storage context")
                storage_context = StorageContext.from_defaults(vector_store=vector_store)
            
            # Create temporary index to get embeddings
            temp_index = VectorStoreIndex.from_documents(
                documents,
                storage_context=storage_context,
                show_progress=True
            )
            
            # Persist the storage context (this saves docstore, etc.)
            temp_index.storage_context.persist(self.index_dir)
            
            # Track vector IDs for this document
            start_id = self._mapping["next_id"]
            num_vectors = len(documents)
            vector_ids = list(range(start_id, start_id + num_vectors))
            
            # Update mapping
            self._mapping["documents"][doc_path] = {
                "vector_ids": vector_ids,
                "num_chunks": num_vectors,
                "indexed_at": datetime.now().isoformat(),
                "file_name": os.path.basename(doc_path)
            }
            self._mapping["next_id"] = start_id + num_vectors
            
            # Save mapping and index
            self._save_mapping()
            self._save_faiss_index()
            
            return {
                "success": True,
                "document": doc_path,
                "vectors_added": num_vectors
            }
            
        except Exception as e:
            logger.error(f"Error adding document {doc_path}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def remove_document(self, doc_path: str) -> Dict:
        """Remove a document and its vectors from the index"""
        try:
            if doc_path not in self._mapping["documents"]:
                return {
                    "success": False,
                    "error": "Document not found in index"
                }
            
            doc_info = self._mapping["documents"][doc_path]
            vector_ids = doc_info["vector_ids"]
            
            # For FAISS flat index, we need to rebuild without the removed vectors
            # This is more complex but maintains consistency
            faiss_index = self.get_faiss_index()
            
            if faiss_index.ntotal > 0:
                # Get all vectors
                all_vectors = faiss_index.reconstruct_n(0, faiss_index.ntotal)
                
                # Create mask for vectors to keep
                keep_mask = np.ones(faiss_index.ntotal, dtype=bool)
                for vid in vector_ids:
                    if vid < faiss_index.ntotal:
                        keep_mask[vid] = False
                
                # Create new index with remaining vectors
                new_index = faiss.IndexFlatL2(settings.EMBEDDING_DIM)
                remaining_vectors = all_vectors[keep_mask]
                
                if len(remaining_vectors) > 0:
                    new_index.add(remaining_vectors)
                
                # Replace the index
                self._faiss_index = new_index
                self._vector_store = None  # Reset vector store
                
                # Update mappings - adjust vector IDs
                self._update_mappings_after_removal(doc_path, vector_ids)
            
            # Remove from mapping
            del self._mapping["documents"][doc_path]
            
            # Save updated index and mapping
            self._save_faiss_index()
            self._save_mapping()
            
            return {
                "success": True,
                "document": doc_path,
                "vectors_removed": len(vector_ids)
            }
            
        except Exception as e:
            logger.error(f"Error removing document {doc_path}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _update_mappings_after_removal(self, removed_doc: str, removed_ids: List[int]):
        """Update vector ID mappings after removal"""
        min_removed = min(removed_ids)
        
        # Adjust vector IDs for remaining documents
        for doc_path, doc_info in self._mapping["documents"].items():
            if doc_path != removed_doc:
                # Decrease IDs that were after the removed ones
                updated_ids = []
                for vid in doc_info["vector_ids"]:
                    if vid > min_removed:
                        # Count how many removed IDs were before this one
                        offset = sum(1 for rid in removed_ids if rid < vid)
                        updated_ids.append(vid - offset)
                    else:
                        updated_ids.append(vid)
                doc_info["vector_ids"] = updated_ids
        
        # Update next_id
        self._mapping["next_id"] -= len(removed_ids)
    
    def _save_faiss_index(self):
        """Save FAISS index to disk"""
        faiss_index = self.get_faiss_index()
        if faiss_index:
            os.makedirs(self.index_dir, exist_ok=True)
            faiss.write_index(faiss_index, self.faiss_index_path)
    
    def get_document_info(self) -> Dict:
        """Get information about all indexed documents"""
        return {
            "total_documents": len(self._mapping["documents"]),
            "total_vectors": self._mapping["next_id"],
            "documents": {
                doc_path: {
                    "file_name": info["file_name"],
                    "num_chunks": info["num_chunks"],
                    "indexed_at": info["indexed_at"]
                }
                for doc_path, info in self._mapping["documents"].items()
            }
        }
    
    def rebuild_full_index(self, documents_by_path: Dict[str, List[Document]]) -> Dict:
        """Rebuild the entire index from scratch"""
        try:
            # Reset everything
            self._faiss_index = faiss.IndexFlatL2(settings.EMBEDDING_DIM)
            self._vector_store = None
            self._mapping = {"documents": {}, "next_id": 0}
            
            # Create new vector store and storage context
            vector_store = self.get_vector_store()
            storage_context = StorageContext.from_defaults(
                vector_store=vector_store,
                persist_dir=self.index_dir
            )
            
            # Combine all documents for single index creation
            all_documents = []
            for documents in documents_by_path.values():
                all_documents.extend(documents)
            
            if all_documents:
                # Create the index with all documents at once
                index = VectorStoreIndex.from_documents(
                    all_documents,
                    storage_context=storage_context,
                    show_progress=True
                )
                
                # Persist the storage context
                index.storage_context.persist(self.index_dir)
                
                # Update mapping for all documents
                vector_id = 0
                for doc_path, documents in documents_by_path.items():
                    num_vectors = len(documents)
                    vector_ids = list(range(vector_id, vector_id + num_vectors))
                    
                    self._mapping["documents"][doc_path] = {
                        "vector_ids": vector_ids,
                        "num_chunks": num_vectors,
                        "indexed_at": datetime.now().isoformat(),
                        "file_name": os.path.basename(doc_path)
                    }
                    vector_id += num_vectors
                
                self._mapping["next_id"] = vector_id
                
                # Save mapping and index
                self._save_mapping()
                self._save_faiss_index()
            
            return {
                "success": True,
                "documents_indexed": len(documents_by_path),
                "total_vectors": self._mapping["next_id"]
            }
            
        except Exception as e:
            logger.error(f"Error rebuilding index: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def is_document_indexed(self, doc_path: str) -> bool:
        """Check if a document is already indexed"""
        return doc_path in self._mapping["documents"]