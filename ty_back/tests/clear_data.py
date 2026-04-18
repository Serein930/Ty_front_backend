import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.milvus import delete_all_data, get_collection

def clear_data():
    print("=== Clear All Data ===")
    delete_all_data()
    collection = get_collection()
    print(f"Collection '{collection.name}' cleared. Entities: {collection.num_entities}")

if __name__ == "__main__":
    clear_data()
