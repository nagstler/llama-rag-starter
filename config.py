# config.py

import os

# === File Paths ===
DATA_DIR = "data"
INDEX_DIR = "index"

# === OpenAI ===
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
EMBEDDING_MODEL = "text-embedding-ada-002"
LLM_MODEL = "gpt-3.5-turbo"

# === Vector dimensions (based on embedding model) ===
EMBEDDING_DIM = 1536
