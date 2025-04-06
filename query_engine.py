# query_engine.py

import faiss
import config
from llama_index.core import load_index_from_storage
from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.core.storage import StorageContext
from llama_index.llms.openai import OpenAI

def load_query_engine():
    print("🔄 Loading FAISS index manually...")

    # Load the saved FAISS index
    faiss_index_path = f"{config.INDEX_DIR}/faiss.index"
    faiss_index = faiss.read_index(faiss_index_path)

    vector_store = FaissVectorStore(faiss_index=faiss_index)
    storage_context = StorageContext.from_defaults(
        persist_dir=config.INDEX_DIR,
        vector_store=vector_store
    )

    index = load_index_from_storage(storage_context)
    query_engine = index.as_query_engine(llm=OpenAI(model=config.LLM_MODEL))

    return query_engine
