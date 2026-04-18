import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pymilvus import connections, utility

from app.milvus import get_collection
from app.milvus.config import milvus_settings

connections.connect(host=milvus_settings.HOST, port=milvus_settings.PORT, alias="default")


def format_publish_time(timestamp: int) -> str:
    if not timestamp:
        return "N/A"
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def query_topic_collection(topic_id: str):
    collection_name = f"topic_{topic_id}"
    print(f"\n{'='*60}")
    print(f"Querying topic collection: {collection_name}")
    print(f"{'='*60}")

    if not utility.has_collection(collection_name):
        print(f"Collection '{collection_name}' does not exist!")
        return

    collection = get_collection(collection_name)
    print(f"Collection '{collection_name}' exists: Yes")
    print(f"Total entities: {collection.num_entities}")

    output_fields = [
        "content_id", "title", "text_preview", "raw_content", "chunk_index", "publish_time",
        "platform", "site_name", "author_name", "threat_category",
        "risk_level", "industry", "risk_score", "region", "url"
    ]

    try:
        results = collection.query(
            expr="id >= 0",
            output_fields=output_fields,
            limit=1000,
            offset=0
        )

        print(f"\nFound {len(results)} items:")
        print("-" * 60)

        content_ids_seen = set()
        for i, item in enumerate(results):
            content_id = item.get("content_id", "")

            if content_id not in content_ids_seen:
                content_ids_seen.add(content_id)
                print(f"\n[Content {len(content_ids_seen)}] {content_id}")
                print(f"  Title: {item.get('title', 'N/A')}")
                print(f"  Threat Category: {item.get('threat_category', 'N/A')}")
                print(f"  Risk Level: {item.get('risk_level', 'N/A')}")
                print(f"  Risk Score: {item.get('risk_score', 'N/A')}")
                print(f"  Region: {item.get('region', 'N/A')}")
                print(f"  Industry: {item.get('industry', 'N/A')}")
                print(f"  Platform: {item.get('platform', 'N/A')}")
                print(f"  Site Name: {item.get('site_name', 'N/A')}")
                print(f"  Publish Time: {format_publish_time(item.get('publish_time', 0))}")
                print(f"  URL: {item.get('url', 'N/A')}")
                print(f"  Text Preview: {item.get('text_preview', 'N/A')[:100]}...")
            else:
                print(f"  [Chunk {item.get('chunk_index', 0)}] {item.get('raw_content', '')[:80]}...")

        print(f"\n{'='*60}")
        print(f"Total unique content IDs: {len(content_ids_seen)}")
        print(f"Total chunks (including duplicates): {len(results)}")

    except Exception as e:
        print(f"Error querying collection: {e}")
        import traceback
        traceback.print_exc()

    print(f"{'='*60}\n")


def list_all_topic_collections():
    print(f"\n{'='*60}")
    print("Listing all collections in Milvus")
    print(f"{'='*60}")

    try:
        collections = utility.list_collections()
        print(f"All collections: {collections}")

        topic_collections = [c for c in collections if c.startswith("topic_")]
        print(f"\nTopic collections (prefix 'topic_'):")
        for tc in topic_collections:
            print(f"  - {tc}")

        if not topic_collections:
            print(f"  (none)")

    except Exception as e:
        print(f"Error listing collections: {e}")

    print(f"{'='*60}\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Query topic collection data")
    parser.add_argument("--topic-id", "-t", type=str, help="Topic collection ID to query")
    parser.add_argument("--list", "-l", action="store_true", help="List all collections")

    args = parser.parse_args()

    if args.list:
        list_all_topic_collections()
    elif args.topic_id:
        query_topic_collection(args.topic_id)
    else:
        print("Usage:")
        print("  python tests/verify_topic_data.py --list                    # List all collections")
        print("  python tests/verify_topic_data.py --topic-id <topic_id>     # Query specific topic collection")
        print("\nExamples:")
        print("  python tests/verify_topic_data.py --list")
        print("  python tests/verify_topic_data.py -t 1776393458635")
        print("  python tests/verify_topic_data.py --topic-id 1776393458635")