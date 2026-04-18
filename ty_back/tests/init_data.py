import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.milvus import create_ty_content_collection, insert_chunks, get_collection
from app.milvus.config import milvus_settings
from pymilvus import utility


def init_data():
    print("=== Initialize Data ===")

    get_collection()

    if utility.has_collection(milvus_settings.COLLECTION_NAME):
        print(f"Dropping existing collection '{milvus_settings.COLLECTION_NAME}'...")
        utility.drop_collection(milvus_settings.COLLECTION_NAME)

    create_ty_content_collection()
    print(f"Collection '{milvus_settings.COLLECTION_NAME}' created with 17 fields (including title, text_preview)!")

    chunks = [
        "攻击者利用零日漏洞入侵企业内网，窃取大量敏感数据。",
        "建议立即更新所有系统的安全补丁，并加强网络监控。",
        "受影响的系统包括Windows服务器和Linux数据库服务器。",
    ]
    metadata = {
        "publish_time": datetime(2024, 1, 15, 10, 30, 0),
        "platform": "SecurityNews",
        "site_name": "网络安全资讯站",
        "author_name": "安全分析师",
        "threat_category": "数据泄露",
        "risk_level": "高危",
        "industry": "金融",
        "risk_score": 95.5,
        "region": "亚太",
        "url": "https://security.example.com/article/123",
        "text_preview": "监测到重大网络安全威胁，涉及高危漏洞，建议立即处置。"
    }

    pk_list = insert_chunks("test_content_001", "重大网络安全威胁预警", chunks, metadata)
    print(f"Inserted {len(pk_list)} chunks, PKs: {pk_list}")


if __name__ == "__main__":
    init_data()
