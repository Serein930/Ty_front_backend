import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pymilvus import connections, utility, Collection

from app.milvus.config import milvus_settings

connections.connect(host=milvus_settings.HOST, port=milvus_settings.PORT, alias="default")


def format_publish_time(timestamp: int) -> str:
    if not timestamp:
        return "N/A"
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def query_collection_by_name(collection_name: str):
    print(f"\n{'='*60}")
    print(f"Querying collection: {collection_name}")
    print(f"{'='*60}")

    if not utility.has_collection(collection_name):
        print(f"Collection '{collection_name}' does NOT exist!")
        return

    print(f"Collection '{collection_name}' exists: Yes")

    collection = Collection(name=collection_name)
    collection.load()
    print(f"Total entities: {collection.num_entities}")

    output_fields = [
        "id", "content_id", "title", "text_preview", "raw_content", "chunk_index", "publish_time",
        "platform", "site_name", "author_name", "threat_category",
        "risk_level", "industry", "risk_score", "region", "url"
    ]

    try:
        results = collection.query(
            expr="id >= 0",
            output_fields=output_fields,
            limit=10000,
            offset=0
        )

        print(f"\n{'='*60}")
        print(f"Found {len(results)} total rows")
        print(f"{'='*60}")

        for i, item in enumerate(results):
            print(f"\n--- Row {i+1} ---")
            for field in output_fields:
                value = item.get(field)
                if field == "publish_time":
                    value = f"{value} ({format_publish_time(value)})"
                elif field == "raw_content" and value:
                    value = value[:200] + "..." if len(value) > 200 else value
                print(f"  {field}: {value}")

        print(f"\n{'='*60}")
        print(f"Total rows printed: {len(results)}")
        print(f"{'='*60}\n")

    except Exception as e:
        print(f"Error querying collection: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Query a Milvus collection by name")
    parser.add_argument("collection_name", type=str, help="Collection name to query")

    args = parser.parse_args()

    query_collection_by_name(args.collection_name)