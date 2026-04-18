import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.milvus import (
    create_ty_content_collection,
    insert_chunks,
    get_collection,
    get_main_collection,
    create_topic_collection,
    check_topic_match,
    sync_topic_data,
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
        {
            "content_id": "content_003",
            "title": "非法走私活动",
            "chunks": ["海关查获重大走私案件", "涉及违规商品数量巨大"],
            "metadata": {
                "publish_time": datetime(2024, 1, 17, 9, 0, 0),
                "platform": "CustomsNews",
                "site_name": "海关资讯",
                "author_name": "记者C",
                "threat_category": "非法走私",
                "risk_level": "MEDIUM",
                "industry": "贸易",
                "risk_score": 60.0,
                "region": "上海",
                "url": "https://example.com/3",
                "text_preview": "重大走私活动监测报告",
            }
        },
        {
            "content_id": "content_004",
            "title": "数据泄露事件",
            "chunks": ["某公司发生重大数据泄露", "影响用户数量超过百万"],
            "metadata": {
                "publish_time": datetime(2024, 1, 18, 16, 45, 0),
                "platform": "SecurityNews",
                "site_name": "网络安全资讯站",
                "author_name": "安全分析师",
                "threat_category": "数据泄露",
                "risk_level": "HIGH",
                "industry": "互联网",
                "risk_score": 88.0,
                "region": "广东",
                "url": "https://example.com/4",
                "text_preview": "重大数据泄露安全事件",
            }
        },
        {
            "content_id": "content_005",
            "title": "金融诈骗预警",
            "chunks": ["近期金融诈骗案件高发", "建议公众提高警惕"],
            "metadata": {
                "publish_time": datetime(2024, 1, 19, 11, 30, 0),
                "platform": "FinanceNews",
                "site_name": "金融资讯网",
                "author_name": "金融分析师",
                "threat_category": "金融诈骗",
                "risk_level": "MEDIUM",
                "industry": "金融",
                "risk_score": 55.0,
                "region": "浙江",
                "url": "https://example.com/5",
                "text_preview": "金融诈骗防范预警",
            }
        },
    ]

    total_inserted = 0
    for item in test_data:
        pk_list = insert_chunks(
            item["content_id"],
            item["title"],
            item["chunks"],
            item["metadata"]
        )
        total_inserted += len(pk_list)
        print(f"  Inserted {len(pk_list)} chunks for {item['content_id']}")

    print(f"\nTotal inserted: {total_inserted} chunks")
    return len(test_data)


def test_check_topic_match():
    print("\n=== Testing check_topic_match ===")

    topic_config = {
        "basic_config": {
            "threat_category": ["毒品交易"],
            "risk_level": "HIGH",
            "risk_score": 0,
            "region": [""],
            "industry": [""],
        }
    }

    test_items = [
        {
            "content_id": "content_001",
            "threat_category": "毒品交易",
            "risk_level": "HIGH",
            "risk_score": 95.0,
            "region": "广东",
            "industry": "金融",
        },
        {
            "content_id": "content_002",
            "threat_category": "毒品相关",
            "risk_level": "LOW",
            "risk_score": 30.0,
            "region": "北京",
            "industry": "教育",
        },
        {
            "content_id": "content_004",
            "threat_category": "数据泄露",
            "risk_level": "HIGH",
            "risk_score": 88.0,
            "region": "广东",
            "industry": "互联网",
        },
    ]

    expected_results = [True, False, False]

    for i, item in enumerate(test_items):
        result = check_topic_match(topic_config, item)
        status = "✓" if result == expected_results[i] else "✗"
        print(f"  {status} content_id={item['content_id']}, expected={expected_results[i]}, got={result}")


def test_sync_topic():
    print("\n=== Testing sync_topic_data ===")

    topic_id = "test_topic_001"
    topic_config = {
        "basic_config": {
            "threat_category": ["毒品交易"],
            "risk_level": "HIGH",
            "risk_score": 0,
            "region": [""],
            "industry": [""],
        }
    }

    if utility.has_collection(topic_id):
        utility.drop_collection(topic_id)
        print(f"Dropped existing topic collection '{topic_id}'")

    total_count, matched_count, last_publish_time, last_content_id = sync_topic_data(
        topic_id, topic_config
    )

    print(f"  Total items scanned: {total_count}")
    print(f"  Matched items: {matched_count}")
    print(f"  Last publish time: {last_publish_time}")
    print(f"  Last content ID: {last_content_id}")

    if last_publish_time:
        dt = datetime.fromtimestamp(last_publish_time)
        print(f"  Last publish time (readable): {dt.strftime('%Y-%m-%d %H:%M:%S')}")

    topic_collection = get_collection(topic_id)
    if topic_collection:
        print(f"  Topic collection '{topic_id}' exists: Yes")
        print(f"  Topic collection row count: {topic_collection.num_entities}")
    else:
        print(f"  Topic collection '{topic_id}' exists: No")

    if utility.has_collection(topic_id):
        utility.drop_collection(topic_id)
        print(f"Cleaned up topic collection '{topic_id}'")


def test_sync_topic_multi_conditions():
    print("\n=== Testing sync_topic with multiple conditions ===")

    topic_id = "test_topic_002"
    topic_config = {
        "basic_config": {
            "threat_category": ["非法走私"],
            "risk_level": "MEDIUM",
            "risk_score": 50,
            "region": ["上海", "广东"],
            "industry": [""],
        }
    }

    if utility.has_collection(topic_id):
        utility.drop_collection(topic_id)
        print(f"Dropped existing topic collection '{topic_id}'")

    total_count, matched_count, last_publish_time, last_content_id = sync_topic_data(
        topic_id, topic_config
    )

    print(f"  Topic filter: threat_category=['非法走私'], risk_level=MEDIUM, risk_score>=50, region in [上海, 广东]")
    print(f"  Total items scanned: {total_count}")
    print(f"  Matched items: {matched_count}")
    print(f"  Last publish time: {last_publish_time}")
    print(f"  Last content ID: {last_content_id}")

    topic_collection = get_collection(topic_id)
    if topic_collection:
        print(f"  Topic collection '{topic_id}' row count: {topic_collection.num_entities}")
    else:
        print(f"  Topic collection '{topic_id}' exists: No")

    if utility.has_collection(topic_id):
        utility.drop_collection(topic_id)
        print(f"Cleaned up topic collection '{topic_id}'")


def cleanup():
    print("\n=== Cleaning up ===")
    if utility.has_collection(milvus_settings.COLLECTION_NAME):
        utility.drop_collection(milvus_settings.COLLECTION_NAME)
        print(f"Dropped main collection '{milvus_settings.COLLECTION_NAME}'")


if __name__ == "__main__":
    try:
        num_contents = create_test_main_data()
        print(f"\n=== Created {num_contents} test contents in main collection ===")

        test_check_topic_match()

        test_sync_topic()

        test_sync_topic_multi_conditions()

        print("\n" + "="*60)
        print("All tests completed!")
        print("="*60)

    except Exception as e:
        print(f"\nError occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cleanup()