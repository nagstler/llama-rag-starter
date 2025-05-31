# src/core/query.py

import faiss
from llama_index.core import load_index_from_storage
from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.core.storage import StorageContext
from llama_index.llms.openai import OpenAI
from config import settings

def load_query_engine():
    print("🔄 Loading FAISS index manually...")

    # Load the saved FAISS index
    faiss_index_path = f"{settings.INDEX_DIR}/faiss.index"
    faiss_index = faiss.read_index(faiss_index_path)
    print(f"✅ FAISS index loaded with {faiss_index.ntotal} vectors")

    vector_store = FaissVectorStore(faiss_index=faiss_index)
    storage_context = StorageContext.from_defaults(
        persist_dir=settings.INDEX_DIR,
        vector_store=vector_store
    )

    index = load_index_from_storage(storage_context)
    query_engine = index.as_query_engine(
        llm=OpenAI(model=settings.LLM_MODEL),
        similarity_top_k=5
    )
    print("✅ Query engine loaded successfully")

    return query_engine