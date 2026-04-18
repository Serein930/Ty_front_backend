from typing import Any, Dict, List, Optional, Tuple

import httpx
from pymilvus import (
    Collection,
    CollectionSchema,
    DataType,
    FieldSchema,
    connections,
    utility,
)

from app.milvus.config import milvus_settings

RISK_LEVEL_PRIORITY = {
    "HIGH": 3,
    "MEDIUM": 2,
    "LOW": 1,
}


def get_embedding(text: str, timeout_seconds: float = 30.0) -> List[float]:
    url = milvus_settings.EMBEDDING_API_URL.rstrip("/")
    payload = {
        "input": text,
        "model": "embedding-model"
    }
    headers = {
        "Content-Type": "application/json",
    }

    with httpx.Client(timeout=timeout_seconds) as client:
        response = client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()
        return result["data"][0]["embedding"]


def create_ty_content_collection() -> Collection:
    connections.connect(
        host=milvus_settings.HOST,
        port=milvus_settings.PORT,
        alias="default"
    )

    if utility.has_collection(milvus_settings.COLLECTION_NAME):
        utility.drop_collection(milvus_settings.COLLECTION_NAME)

    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="content_id", dtype=DataType.VARCHAR, max_length=128),
        FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=512),
        FieldSchema(name="text_preview", dtype=DataType.VARCHAR, max_length=2048),
        FieldSchema(name="raw_content", dtype=DataType.VARCHAR, max_length=65535),
        FieldSchema(name="chunk_index", dtype=DataType.INT64),
        FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=milvus_settings.DIMENSION),
        FieldSchema(name="publish_time", dtype=DataType.INT64),
        FieldSchema(name="platform", dtype=DataType.VARCHAR, max_length=64),
        FieldSchema(name="site_name", dtype=DataType.VARCHAR, max_length=256),
        FieldSchema(name="author_name", dtype=DataType.VARCHAR, max_length=256),
        FieldSchema(name="threat_category", dtype=DataType.VARCHAR, max_length=128),
        FieldSchema(name="risk_level", dtype=DataType.VARCHAR, max_length=64),
        FieldSchema(name="industry", dtype=DataType.VARCHAR, max_length=128),
        FieldSchema(name="risk_score", dtype=DataType.FLOAT),
        FieldSchema(name="region", dtype=DataType.VARCHAR, max_length=128),
        FieldSchema(name="url", dtype=DataType.VARCHAR, max_length=1024),
    ]

    schema = CollectionSchema(fields=fields, description="Threat intelligence content collection")
    collection = Collection(name=milvus_settings.COLLECTION_NAME, schema=schema)

    index_params = {
        "index_type": "IVF_FLAT",
        "metric_type": "L2",
        "params": {"nlist": 128}
    }
    collection.create_index(field_name="vector", index_params=index_params)
    collection.load()

    return collection


def get_collection(collection_name: str = None) -> Collection:
    connections.connect(
        host=milvus_settings.HOST,
        port=milvus_settings.PORT,
        alias="default"
    )
    if collection_name is None:
        collection_name = milvus_settings.COLLECTION_NAME
    if not utility.has_collection(collection_name):
        if collection_name == milvus_settings.COLLECTION_NAME:
            return create_ty_content_collection()
        return None
    return Collection(name=collection_name)


def get_main_collection() -> Collection:
    return get_collection(milvus_settings.COLLECTION_NAME)


def insert_chunks(
    content_id: str,
    title: str,
    chunks: List[str],
    metadata: Dict[str, Any]
) -> List[int]:
    collection = get_collection()

    texts_with_title = [f"{title}\n{chunk}" for chunk in chunks]
    vectors = [get_embedding(text) for text in texts_with_title]

    publish_time = metadata.get("publish_time")
    if publish_time:
        if hasattr(publish_time, 'timestamp'):
            publish_time = int(publish_time.timestamp())
        elif isinstance(publish_time, str):
            from datetime import datetime
            dt = datetime.strptime(publish_time, "%Y-%m-%d %H:%M:%S.%f")
            publish_time = int(dt.timestamp())
        else:
            publish_time = int(publish_time)

    data = [
        [content_id] * len(chunks),
        [title] * len(chunks),
        [metadata.get("text_preview", "")] * len(chunks),
        [chunk for chunk in chunks],
        list(range(len(chunks))),
        vectors,
        [publish_time] * len(chunks) if publish_time else [0] * len(chunks),
        [metadata.get("platform", "UNKNOWN")] * len(chunks),
        [metadata.get("site_name", "")] * len(chunks),
        [metadata.get("author_name", "")] * len(chunks),
        [metadata.get("threat_category", "UNKNOWN")] * len(chunks),
        [metadata.get("risk_level", "UNKNOWN")] * len(chunks),
        [metadata.get("industry", "")] * len(chunks),
        [metadata.get("risk_score", 0.0)] * len(chunks),
        [metadata.get("region", "")] * len(chunks),
        [metadata.get("url", "")] * len(chunks),
    ]

    result = collection.insert(data)
    collection.flush()
    return result.primary_keys


def delete_all_data() -> bool:
    collection = get_collection()
    expr = "id >= 0"
    collection.delete(expr)
    collection.flush()
    return True


def query_content(query: str) -> Dict[str, Any]:
    results = search_vectors(query, top_k=1)
    if results:
        return results[0]
    return {}


def search_vectors(query_text: str, top_k: int = 1, expr: str = None) -> List[Dict[str, Any]]:
    collection = get_collection()
    query_vector = get_embedding(query_text)

    search_params = {
        "metric_type": "L2",
        "params": {"nprobe": 10}
    }

    output_fields = [
        "id", "content_id", "title", "text_preview", "raw_content", "chunk_index", "publish_time",
        "platform", "site_name", "author_name", "threat_category",
        "risk_level", "industry", "risk_score", "region", "url"
    ]

    results = collection.search(
        data=[query_vector],
        anns_field="vector",
        param=search_params,
        limit=top_k,
        expr=expr,
        output_fields=output_fields
    )

    search_results = []
    for hits in results:
        for hit in hits:
            search_results.append({
                "id": hit.id,
                "distance": hit.distance,
                "content_id": hit.entity.get("content_id"),
                "title": hit.entity.get("title"),
                "text_preview": hit.entity.get("text_preview"),
                "raw_content": hit.entity.get("raw_content"),
                "chunk_index": hit.entity.get("chunk_index"),
                "publish_time": hit.entity.get("publish_time"),
                "platform": hit.entity.get("platform"),
                "site_name": hit.entity.get("site_name"),
                "author_name": hit.entity.get("author_name"),
                "threat_category": hit.entity.get("threat_category"),
                "risk_level": hit.entity.get("risk_level"),
                "industry": hit.entity.get("industry"),
                "risk_score": hit.entity.get("risk_score"),
                "region": hit.entity.get("region"),
                "url": hit.entity.get("url"),
            })
    return search_results


def create_topic_collection(topic_id: str) -> Collection:
    connections.connect(
        host=milvus_settings.HOST,
        port=milvus_settings.PORT,
        alias="default"
    )

    collection_name = f"topic_{topic_id}"

    if utility.has_collection(collection_name):
        utility.drop_collection(collection_name)

    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="content_id", dtype=DataType.VARCHAR, max_length=128),
        FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=512),
        FieldSchema(name="text_preview", dtype=DataType.VARCHAR, max_length=2048),
        FieldSchema(name="raw_content", dtype=DataType.VARCHAR, max_length=65535),
        FieldSchema(name="chunk_index", dtype=DataType.INT64),
        FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=milvus_settings.DIMENSION),
        FieldSchema(name="publish_time", dtype=DataType.INT64),
        FieldSchema(name="platform", dtype=DataType.VARCHAR, max_length=64),
        FieldSchema(name="site_name", dtype=DataType.VARCHAR, max_length=256),
        FieldSchema(name="author_name", dtype=DataType.VARCHAR, max_length=256),
        FieldSchema(name="threat_category", dtype=DataType.VARCHAR, max_length=128),
        FieldSchema(name="risk_level", dtype=DataType.VARCHAR, max_length=64),
        FieldSchema(name="industry", dtype=DataType.VARCHAR, max_length=128),
        FieldSchema(name="risk_score", dtype=DataType.FLOAT),
        FieldSchema(name="region", dtype=DataType.VARCHAR, max_length=128),
        FieldSchema(name="url", dtype=DataType.VARCHAR, max_length=1024),
    ]

    schema = CollectionSchema(fields=fields, description=f"Topic collection {topic_id}")
    collection = Collection(name=collection_name, schema=schema)

    index_params = {
        "index_type": "IVF_FLAT",
        "metric_type": "L2",
        "params": {"nlist": 128}
    }
    collection.create_index(field_name="vector", index_params=index_params)
    collection.load()

    return collection


def check_topic_match(topic_config: Dict[str, Any], item: Dict[str, Any]) -> bool:
    basic_config = topic_config.get("basic_config", {})
    threat_categories = basic_config.get("threat_category", [])
    risk_level = basic_config.get("risk_level")
    risk_score = basic_config.get("risk_score")
    regions = basic_config.get("region", [])
    industries = basic_config.get("industry", [])

    print(f"[DEBUG check_topic_match] item content_id={item.get('content_id')}")
    print(f"[DEBUG] threat_categories={threat_categories}, item_threat={item.get('threat_category')}")
    print(f"[DEBUG] risk_level={risk_level}, item_risk_level={item.get('risk_level')}")
    print(f"[DEBUG] risk_score={risk_score}, item_risk_score={item.get('risk_score')}")
    print(f"[DEBUG] regions={regions}, item_region={item.get('region')}")
    print(f"[DEBUG] industries={industries}, item_industry={item.get('industry')}")

    if threat_categories:
        item_threat = item.get("threat_category", "")
        match = any(tc in item_threat for tc in threat_categories if tc)
        print(f"[DEBUG] threat_categories check: {match}")
        if not match:
            return False

    if risk_level:
        item_risk_level = item.get("risk_level", "")
        topic_level_priority = RISK_LEVEL_PRIORITY.get(risk_level.upper(), 0)
        item_level_priority = RISK_LEVEL_PRIORITY.get(item_risk_level.upper(), 0)
        print(f"[DEBUG] risk_level check: topic_priority={topic_level_priority}, item_priority={item_level_priority}, pass={item_level_priority >= topic_level_priority}")
        if item_level_priority < topic_level_priority:
            return False

    if risk_score is not None and risk_score > 0:
        item_risk_score = item.get("risk_score", 0)
        print(f"[DEBUG] risk_score check: item_risk_score={item_risk_score} >= {risk_score} = {item_risk_score >= risk_score}")
        if item_risk_score < risk_score:
            return False

    if regions:
        item_region = item.get("region", "")
        valid_regions = [r for r in regions if r]
        if valid_regions:
            if not item_region or not any(r in item_region for r in valid_regions):
                return False

    if industries:
        item_industry = item.get("industry", "")
        valid_industries = [ind for ind in industries if ind]
        if valid_industries:
            if not item_industry or not any(ind in item_industry for ind in valid_industries):
                return False

    print(f"[DEBUG] item {item.get('content_id')} MATCHED!")
    return True


def sync_topic_data(topic_id: str, topic_config: Dict[str, Any]) -> Tuple[int, int, int, str]:
    print(f"\n{'='*60}")
    print(f"[SYNC] Starting topic sync: topic_id={topic_id}")
    print(f"[SYNC] Topic config: {topic_config.get('name', 'N/A')}")
    basic = topic_config.get("basic_config", {})
    print(f"[SYNC] Filter conditions:")
    print(f"       threat_category: {basic.get('threat_category', [])}")
    print(f"       risk_level: {basic.get('risk_level', 'N/A')}")
    print(f"       risk_score: {basic.get('risk_score', 0)}")
    print(f"       region: {basic.get('region', [])}")
    print(f"       industry: {basic.get('industry', [])}")
    print(f"{'='*60}")

    main_collection = get_main_collection()
    if main_collection is None:
        print(f"[SYNC] ERROR: Main collection not found!")
        return 0, 0, 0, ""

    topic_collection = create_topic_collection(topic_id)
    print(f"[SYNC] Created topic collection: {topic_id}")

    output_fields = [
        "content_id", "title", "text_preview", "raw_content", "chunk_index", "publish_time",
        "platform", "site_name", "author_name", "threat_category",
        "risk_level", "industry", "risk_score", "region", "url"
    ]

    all_data = []
    total_count = 0
    matched_count = 0
    last_publish_time = 0
    last_content_id = ""

    batch_size = 1000
    offset = 0

    print(f"[SYNC] Scanning main collection '{milvus_settings.COLLECTION_NAME}'...")

    while True:
        try:
            results = main_collection.query(
                expr="id >= 0",
                output_fields=output_fields,
                limit=batch_size,
                offset=offset
            )
        except Exception as e:
            print(f"[SYNC] ERROR during query: {e}")
            break

        if not results:
            break

        for item in results:
            total_count += 1
            is_match = check_topic_match(topic_config, item)
            if is_match:
                matched_count += 1
                all_data.append(item)
                print(f"[SYNC]   ✓ MATCH: content_id={item.get('content_id')}, "
                      f"threat={item.get('threat_category')}, "
                      f"level={item.get('risk_level')}, "
                      f"score={item.get('risk_score')}, "
                      f"region={item.get('region')}, "
                      f"industry={item.get('industry')}")
                pub_time = item.get("publish_time", 0)
                if pub_time and pub_time > last_publish_time:
                    last_publish_time = pub_time
                    last_content_id = item.get("content_id", "")

        print(f"[SYNC] Processed batch at offset {offset}, scanned {total_count} items so far...")
        offset += batch_size

    print(f"\n[SYNC] Scan complete: {total_count} total items, {matched_count} matched")

    if all_data:
        print(f"[SYNC] Inserting {len(all_data)} items into topic collection '{topic_id}'...")
        entities = [
            [item.get("content_id", "") for item in all_data],
            [item.get("title", "") for item in all_data],
            [item.get("text_preview", "") for item in all_data],
            [item.get("raw_content", "") for item in all_data],
            [item.get("chunk_index", 0) for item in all_data],
            [[0.0] * milvus_settings.DIMENSION for _ in all_data],
            [item.get("publish_time", 0) for item in all_data],
            [item.get("platform", "") for item in all_data],
            [item.get("site_name", "") for item in all_data],
            [item.get("author_name", "") for item in all_data],
            [item.get("threat_category", "") for item in all_data],
            [item.get("risk_level", "") for item in all_data],
            [item.get("industry", "") for item in all_data],
            [item.get("risk_score", 0.0) for item in all_data],
            [item.get("region", "") for item in all_data],
            [item.get("url", "") for item in all_data],
        ]

        topic_collection.insert(entities)
        topic_collection.flush()
        print(f"[SYNC] Insert complete!")
    else:
        print(f"[SYNC] No items to insert!")

    print(f"[SYNC] Final cursor: last_publish_time={last_publish_time}, last_content_id={last_content_id}")
    print(f"{'='*60}\n")

    return total_count, matched_count, last_publish_time, last_content_id
