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


def query_main_collection():
    print(f"\n{'='*60}")
    print(f"Querying main collection: {milvus_settings.COLLECTION_NAME}")
    print(f"{'='*60}")

    if not utility.has_collection(milvus_settings.COLLECTION_NAME):
        print(f"Collection '{milvus_settings.COLLECTION_NAME}' does not exist!")
        return

    collection = get_collection()
    print(f"Collection exists: Yes")
    print(f"Total entities: {collection.num_entities}")

    output_fields = [
        "content_id", "title", "threat_category", "risk_level",
        "risk_score", "region", "industry", "publish_time"
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

        seen = set()
        for item in results:
            content_id = item.get("content_id", "")
            if content_id in seen:
                continue
            seen.add(content_id)

            print(f"\ncontent_id: {content_id}")
            print(f"  title: {item.get('title', 'N/A')}")
            print(f"  threat_category: {item.get('threat_category', 'N/A')}")
            print(f"  risk_level: {item.get('risk_level', 'N/A')}")
            print(f"  risk_score: {item.get('risk_score', 'N/A')}")
            print(f"  region: {item.get('region', 'N/A')}")
            print(f"  industry: {item.get('industry', 'N/A')}")
            print(f"  publish_time: {format_publish_time(item.get('publish_time', 0))}")

        print(f"\n{'='*60}")
        print(f"Total unique content IDs: {len(seen)}")
        print(f"Total rows (including chunks): {len(results)}")

    except Exception as e:
        print(f"Error querying collection: {e}")
        import traceback
        traceback.print_exc()

    print(f"{'='*60}\n")


if __name__ == "__main__":
    query_main_collection()