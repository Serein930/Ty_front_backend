from typing import Any, Dict, List, Optional

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



