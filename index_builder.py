# index_builder.py

import os
import faiss
import config
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.core.storage import StorageContext


def build_and_persist_index():
    print("📂 Loading documents from:", config.DATA_DIR)
    documents = SimpleDirectoryReader(config.DATA_DIR, recursive=True).load_data()

    print("🔧 Building vector store...")
    # ✅ create and keep a reference to the faiss_index
    faiss_index = faiss.IndexFlatL2(config.EMBEDDING_DIM)
    vector_store = FaissVectorStore(faiss_index=faiss_index)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    print("📚 Creating index...")
    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context
    )

    print("💾 Saving index to:", config.INDEX_DIR)
    index.storage_context.persist(config.INDEX_DIR)

    # ✅ Save the original FAISS index reference that was actually used
    faiss_path = os.path.join(config.INDEX_DIR, "faiss.index")
    print("📦 Saving index to:", faiss_path)
    faiss.write_index(faiss_index, faiss_path)

    print("✅ Index built and saved.")


if __name__ == "__main__":
    build_and_persist_index()
