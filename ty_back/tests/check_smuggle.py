import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pymilvus import connections, utility, Collection

from app.milvus.config import milvus_settings

connections.connect(host=milvus_settings.HOST, port=milvus_settings.PORT, alias="default")


def query_topic_smuggle():
    print(f"\n{'='*60}")
    print(f"Querying TopicSmuggle items from: {milvus_settings.COLLECTION_NAME}")
    print(f"{'='*60}")

    collection = Collection(name=milvus_settings.COLLECTION_NAME)
    collection.load()

    output_fields = ["content_id", "threat_category", "risk_level", "risk_score", "publish_time"]

    results = collection.query(
        expr='threat_category == "TopicSmuggle"',
        output_fields=output_fields,
        limit=1000,
        offset=0
    )

    print(f"\nFound {len(results)} TopicSmuggle items:\n")

    for i, item in enumerate(results):
        print(f"--- Item {i+1} ---")
        print(f"  content_id: {item.get('content_id')}")
        print(f"  threat_category: {item.get('threat_category')}")
        print(f"  risk_level: {item.get('risk_level')}")
        print(f"  risk_score: {item.get('risk_score')}")
        print()

    print(f"{'='*60}")
    print(f"Total: {len(results)} items")

    print(f"\n--- Risk level breakdown ---")
    from collections import Counter
    levels = [item.get('risk_level') for item in results]
    for level, count in Counter(levels).most_common():
        print(f"  {level}: {count}")

    print(f"\n--- Risk score breakdown ---")
    scores = [item.get('risk_score') for item in results]
    print(f"  min: {min(scores)}")
    print(f"  max: {max(scores)}")

    print(f"\n--- Items that would match risk_level=MEDIUM and risk_score>=60 ---")
    match_count = 0
    for item in results:
        level = item.get('risk_level', '').upper()
        score = item.get('risk_score', 0)
        if level in ['MEDIUM', 'HIGH', 'CRITICAL'] and score >= 60:
            match_count += 1
            print(f"  content_id={item.get('content_id')}, level={level}, score={score}")
    print(f"  Total matchable: {match_count}")


if __name__ == "__main__":
    query_topic_smuggle()