import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.milvus.service import check_topic_match, RISK_LEVEL_PRIORITY

print("=== Testing check_topic_match function ===")
print(f"RISK_LEVEL_PRIORITY: {RISK_LEVEL_PRIORITY}\n")

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

print("Testing with topic_config:")
print(f"  threat_category: {topic_config['basic_config']['threat_category']}")
print(f"  risk_level: {topic_config['basic_config']['risk_level']}")
print(f"  risk_score: {topic_config['basic_config']['risk_score']}")
print()

for i, item in enumerate(test_items):
    result = check_topic_match(topic_config, item)
    status = "✓" if result == expected_results[i] else "✗"
    print(f"  {status} Test {i+1}: content_id={item['content_id']}")
    print(f"      threat_category={item['threat_category']}, risk_level={item['risk_level']}, risk_score={item['risk_score']}")
    print(f"      expected={expected_results[i]}, got={result}")
    print()

print("\n=== Direct check of logic ===")
print("For content_001:")
tc = topic_config["basic_config"]["threat_category"]
print(f"  threat_category check: {tc} vs item threat '{test_items[0]['threat_category']}'")
print(f"  '毒品交易' in '毒品交易': {'毒品交易' in '毒品交易'}")

print("\nFor content_002:")
print(f"  '毒品交易' in '毒品相关': {'毒品交易' in '毒品相关'}")