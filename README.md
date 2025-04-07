# 🧠 llama-rag-starter

> A minimal end-to-end Retrieval-Augmented Generation (RAG) pipeline using [LlamaIndex](https://www.llamaindex.ai/), [FAISS](https://github.com/facebookresearch/faiss), and [OpenAI](https://platform.openai.com/).

This project demonstrates how to build a simple but extensible RAG system that can answer questions from unstructured documents using semantic search and large language models.

---

## Features

- 🔍 Loads unstructured files (PDF, TXT, DOCX) from a local directory  
- ✂️ Automatically chunks and embeds text using OpenAI  
- 📦 Stores vectors in FAISS (local vector store)  
- 🧠 Retrieves relevant chunks using vector similarity  
- 🤖 Uses GPT-3.5 to generate answers grounded in your documents  
- 💻 Clean CLI interface to build and query the index  

---

## 📁 Project Structure

```
llama-rag-starter/
├── app.py                # CLI entry point
├── index_builder.py      # Index construction (chunk + embed)
├── query_engine.py       # Query interface
├── config.py             # Constants and API keys
├── setup.sh              # First-time setup script
├── data/                 # Drop your unstructured docs here
├── index/                # Stores persistent FAISS + metadata
└── requirements.txt      # Python dependencies
```

---

## ⚙️ Setup Instructions

### 1. Clone the repo

```bash
git clone https://github.com/nagstler/llama-rag-starter.git
cd llama-rag-starter
```

### 2. Run setup

```bash
chmod +x setup.sh
./setup.sh
```

This will:
- Set up a Python virtual environment
- Install required packages
- Create `data/` and `index/` folders

### 3. Set your OpenAI API key

```bash
export OPENAI_API_KEY=sk-...
```

---

## 📦 Usage

### 1. Drop Files into `data/`

Supports `.txt`, `.pdf`, `.docx`, and more.

### 2. Run the CLI

```bash
python3 app.py
```

You’ll see:

```
1. Build index
2. Query index
```

- Choose `1` to build the index from documents  
- Choose `2` to ask natural language questions

---

## 🔁 RAG Architecture

```
User Query
   ↓
Embed Query (OpenAI)
   ↓
Vector Search (FAISS)
   ↓
Retrieve Top-k Chunks (LlamaIndex)
   ↓
Build Prompt with Chunks + Query
   ↓
LLM Response (OpenAI GPT-3.5)
```

---

## 🧰 Tech Stack

| Component     | Tool                            |
|---------------|---------------------------------|
| RAG Framework | [LlamaIndex](https://llamaindex.ai) |
| Embeddings    | OpenAI `text-embedding-ada-002` |
| LLM           | OpenAI GPT-3.5                  |
| Vector Store  | FAISS                           |
| Interface     | Python 3 CLI                    |

---

## 📚 Related Resources

- [LlamaIndex Documentation](https://docs.llamaindex.ai/)
- [FAISS GitHub](https://github.com/facebookresearch/faiss)
- [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings)

---

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or pull requests.

---

## 📄 License

MIT License

---

> Built by [@Nagendra Dhanakeerthi](https://github.com/nagstler) • April 2025
