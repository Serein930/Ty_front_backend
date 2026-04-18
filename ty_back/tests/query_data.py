import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.milvus import search_vectors


def format_publish_time(timestamp: int) -> str:
    if not timestamp:
        return "N/A"
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def print_result(result: dict, rank: int = 1):
    print(f"\n{'='*60}")
    print(f"Result #{rank}")
    print(f"{'='*60}")
    print(f"  Distance: {result['distance']:.4f}")
    print(f"  Content ID: {result['content_id']}")
    print(f"  URL: {result['url']}")
    print(f"  Title: {result.get('title', 'N/A')}")
    print(f"  Text Preview: {result.get('text_preview', 'N/A')}")
    print(f"  --- Chunk Info ---")
    print(f"  Chunk Index: {result['chunk_index']}")
    print(f"  Raw Content: {result['raw_content'][:300]}..." if len(result.get('raw_content', '')) > 300 else f"  Raw Content: {result.get('raw_content', '')}")
    print(f"  --- Metadata ---")
    print(f"  Platform: {result['platform']}")
    print(f"  Threat Category: {result['threat_category']}")
    print(f"  Risk Level: {result['risk_level']}")
    print(f"  Risk Score: {result['risk_score']}")
    print(f"  Industry: {result['industry']}")
    print(f"  Region: {result['region']}")
    print(f"  Publish Time: {format_publish_time(result.get('publish_time'))}")


async def main_async():
    query = input("Enter your search query: ").strip()
    if not query:
        query = "匿名筹资服务"
        print(f"Using default query: {query}")

    top_k_input = input("How many results to return (default 3): ").strip()
    top_k = int(top_k_input) if top_k_input else 3

    print(f"\n=== Searching for: {query} (top_k={top_k}) ===")

    results = search_vectors(query, top_k=top_k)

    if results:
        print(f"\nFound {len(results)} results:")
        for idx, result in enumerate(results):
            print_result(result, idx + 1)

        print(f"\n{'='*60}")
        print(f"Summary: {len(results)} results returned, top match distance: {results[0]['distance']:.4f}")
    else:
        print("No results found!")


def main():
    import asyncio
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
