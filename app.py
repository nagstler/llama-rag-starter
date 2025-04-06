# app.py

from index_builder import build_and_persist_index
from query_engine import load_query_engine

def main():
    print("🔁 What would you like to do?")
    print("1. Build index from files")
    print("2. Query the index")
    choice = input("Enter 1 or 2: ").strip()

    if choice == "1":
        build_and_persist_index()

    elif choice == "2":
        engine = load_query_engine()
        print("\n🧠 Ask questions about your data (type 'exit' to quit)\n")

        while True:
            query = input("You: ")
            if query.strip().lower() in {"exit", "quit"}:
                break
            response = engine.query(query)
            print("\n📝 Answer:\n", response, "\n")

    else:
        print("❌ Invalid choice.")

if __name__ == "__main__":
    main()
