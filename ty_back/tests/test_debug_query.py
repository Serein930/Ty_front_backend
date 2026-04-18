import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.milvus import (
    create_ty_content_collection,
    insert_chunks,
    get_collection,
    get_main_collection,
)
from app.milvus.config import milvus_settings
from pymilvus import utility


def create_test_main_data():
    print("\n=== Creating Test Main Collection Data ===")

    get_collection()

    if utility.has_collection(milvus_settings.COLLECTION_NAME):
        print(f"Dropping existing collection '{milvus_settings.COLLECTION_NAME}'...")
        utility.drop_collection(milvus_settings.COLLECTION_NAME)

    create_ty_content_collection()
    print(f"Main collection '{milvus_settings.COLLECTION_NAME}' created!")

    test_data = [
        {
            "content_id": "content_001",
            "title": "毒品交易预警",
            "chunks": ["在边境地区发现大规模毒品交易活动", "涉及走私团伙运作"],
            "metadata": {
                "publish_time": datetime(2024, 1, 15, 10, 30, 0),
                "platform": "SecurityNews",
                "site_name": "安全资讯网",
                "author_name": "分析师A",
                "threat_category": "毒品交易",
                "risk_level": "HIGH",
                "industry": "金融",
                "risk_score": 95.0,
                "region": "广东",
                "url": "https://example.com/1",
                "text_preview": "监测到重大毒品交易预警",
            }
        },
        {
            "content_id": "content_002",
            "title": "一般毒品相关报道",
            "chunks": ["某地发现少量毒品窝点", "已移交公安机关处理"],
            "metadata": {
                "publish_time": datetime(2024, 1, 16, 14, 20, 0),
                "platform": "NewsDaily",
                "site_name": "新闻日报",
                "author_name": "记者B",
                "threat_category": "毒品相关",
                "risk_level": "LOW",
                "industry": "教育",
                "risk_score": 30.0,
                "region": "北京",
                "url": "https://example.com/2",
                "text_preview": "一般毒品案件报道",
            }
        },
    ]

    for item in test_data:
        pk_list = insert_chunks(
            item["content_id"],
            item["title"],
            item["chunks"],
            item["metadata"]
        )
        print(f"  Inserted {len(pk_list)} chunks for {item['content_id']}")

    return len(test_data)


def debug_query():
    print("\n=== Debugging Query ===")

    main_collection = get_main_collection()
    if main_collection is None:
        print("Main collection not found!")
        return

    output_fields = [
        "content_id", "title", "text_preview", "raw_content", "chunk_index", "publish_time",
        "platform", "site_name", "author_name", "threat_category",
        "risk_level", "industry", "risk_score", "region", "url"
    ]

    try:
        results = main_collection.query(
            expr="id >= 0",
            output_fields=output_fields,
            limit=10,
            offset=0
        )
        print(f"Query returned {len(results)} results")
        for i, item in enumerate(results):
            print(f"\n--- Item {i} ---")
            for key in output_fields:
                print(f"  {key}: {item.get(key)}")
    except Exception as e:
        print(f"Query error: {e}")
        import traceback
        traceback.print_exc()


def cleanup():
    print("\n=== Cleaning up ===")
    if utility.has_collection(milvus_settings.COLLECTION_NAME):
        utility.drop_collection(milvus_settings.COLLECTION_NAME)
        print(f"Dropped main collection '{milvus_settings.COLLECTION_NAME}'")


if __name__ == "__main__":
    try:
        num_contents = create_test_main_data()
        print(f"\n=== Created {num_contents} test contents in main collection ===")

        debug_query()

    except Exception as e:
        print(f"\nError occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cleanup()