import sys
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pymilvus import connections, utility, Collection

from app.milvus.config import milvus_settings

connections.connect(host=milvus_settings.HOST, port=milvus_settings.PORT, alias="default")


def analyze_threat_categories(collection_name: str):
    print(f"\n{'='*60}")
    print(f"Analyzing threat_category values in: {collection_name}")
    print(f"{'='*60}")

    if not utility.has_collection(collection_name):
        print(f"Collection '{collection_name}' does NOT exist!")
        return

    collection = Collection(name=collection_name)
    collection.load()
    print(f"Total entities: {collection.num_entities}")

    output_fields = ["threat_category", "risk_level", "risk_score", "content_id"]

    try:
        results = collection.query(
            expr="id >= 0",
            output_fields=output_fields,
            limit=10000,
            offset=0
        )

        threat_categories = [item.get("threat_category", "") for item in results]
        risk_levels = [item.get("risk_level", "") for item in results]
        risk_scores = [item.get("risk_score", 0) for item in results]

        print(f"\n--- threat_category distribution ---")
        for tc, count in Counter(threat_categories).most_common():
            print(f"  {tc}: {count}")

        print(f"\n--- risk_level distribution ---")
        for rl, count in Counter(risk_levels).most_common():
            print(f"  {rl}: {count}")

        print(f"\n--- risk_score range ---")
        valid_scores = [s for s in risk_scores if s is not None]
        if valid_scores:
            print(f"  min: {min(valid_scores)}")
            print(f"  max: {max(valid_scores)}")
            print(f"  avg: {sum(valid_scores)/len(valid_scores):.2f}")

        print(f"\n--- All unique threat_category values ---")
        unique_threats = sorted(set(threat_categories))
        for tc in unique_threats:
            print(f"  - {tc}")

        print(f"\n{'='*60}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("collection_name", nargs="?", default="ty_content")
    args = parser.parse_args()
    analyze_threat_categories(args.collection_name)