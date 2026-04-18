# app/routers/topics.py
import json
import fcntl
from datetime import datetime
from pathlib import Path
from typing import Any, List

from fastapi import APIRouter, HTTPException, Path as PathParam
from pydantic import BaseModel

from app.schemas.topic import SubscriptionTopicCreate, SubscriptionTopicResponse, SubscriptionTopicListItem
from app.schemas.base import Result
from app.milvus import sync_topic_data
from app.milvus.service import get_collection
from app.milvus.config import milvus_settings
from pymilvus import utility, connections

router = APIRouter(prefix="/api/topics", tags=["专题管理"])

TOPICS_FILE = Path(__file__).resolve().parent.parent / "config" / "topics.json"


def update_topic_sync_info(topic_id: str, last_time: int, last_id: str, final_syn_time: str) -> bool:
    try:
        with open(TOPICS_FILE, "r") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                content = f.read()
                if content.strip():
                    topics = json.loads(content)
                    if not isinstance(topics, dict):
                        topics = {}
                else:
                    topics = {}
            except (json.JSONDecodeError, ValueError):
                topics = {}
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)

        if str(topic_id) not in topics:
            return False

        topics[str(topic_id)]["cursor"] = {
            "last_time": last_time,
            "last_id": last_id
        }
        topics[str(topic_id)]["final_syn_time"] = final_syn_time

        with open(TOPICS_FILE, "w") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            json.dump(topics, f, ensure_ascii=False, indent=2)
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)

        return True
    except Exception:
        return False


@router.post("/create", response_model=Result[SubscriptionTopicResponse])
def create_topic(payload: SubscriptionTopicCreate):
    topic_id = int(datetime.now().timestamp() * 1000)

    now = datetime.now()
    if payload.created_at is None:
        created_at = now
    else:
        created_at = payload.created_at

    topic_data = payload.model_dump(mode="json")
    topic_data.pop("id", None)
    topic_data["created_at"] = created_at.isoformat()
    topic_data["updated_at"] = now.isoformat()
    topic_data["last_saved_draft_at"] = now.isoformat()
    topic_data["applied_at"] = now.isoformat()
    topic_data["deleted_at"] = None
    topic_data["final_syn_time"] = None

    for field in ["last_saved_draft_at", "applied_at", "deleted_at", "final_syn_time"]:
        if topic_data.get(field) and isinstance(topic_data[field], datetime):
            topic_data[field] = topic_data[field].isoformat()

    try:
        TOPICS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(TOPICS_FILE, "a+") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.seek(0)
                content = f.read()
                if content.strip():
                    topics = json.loads(content)
                    if not isinstance(topics, dict):
                        topics = {}
                else:
                    topics = {}
            except (json.JSONDecodeError, ValueError):
                topics = {}

            topics[str(topic_id)] = topic_data

            f.seek(0)
            f.truncate()
            json.dump(topics, f, ensure_ascii=False, indent=2)
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"写入 topics.json 失败: {str(e)}")

    topic_data["id"] = topic_id

    if payload.mode == "basic":
        try:
            total_count, matched_count, last_publish_time, last_content_id = sync_topic_data(
                str(topic_id), topic_data
            )
            final_syn_time = datetime.now().isoformat()
            update_topic_sync_info(str(topic_id), last_publish_time, last_content_id, final_syn_time)
            topic_data["cursor"] = {
                "last_time": last_publish_time,
                "last_id": last_content_id
            }
            topic_data["final_syn_time"] = final_syn_time
        except Exception as e:
            print(f"专题 {topic_id} 同步失败: {str(e)}")

    return Result.success(
        data=SubscriptionTopicResponse(**topic_data)
    )


@router.get("/list", response_model=Result[list[SubscriptionTopicListItem]])
def list_topics():
    try:
        with open(TOPICS_FILE, "r") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            content = f.read()
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            if not content.strip():
                return Result.success(data=[])
            topics = json.loads(content)
    except (FileNotFoundError, json.JSONDecodeError):
        return Result.success(data=[])

    result = []
    for topic_id, topic_data in topics.items():
        item = SubscriptionTopicListItem(
            id=int(topic_id),
            name=topic_data.get("name"),
            enabled=topic_data.get("enabled"),
            charge_person=topic_data.get("meta", {}).get("charge_person"),
            summary=topic_data.get("meta", {}).get("summary"),
            final_syn_time=topic_data.get("final_syn_time"),
        )
        result.append(item)

    return Result.success(data=result)


@router.get("/all", response_model=Result[dict])
def get_all_topics_data():
    print(f"\n{'='*60}")
    print(f"[GET ALL TOPICS] Starting fetch all topics data")
    print(f"{'='*60}")

    try:
        with open(TOPICS_FILE, "r") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            content = f.read()
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            if not content.strip():
                return Result.success(data={"topics": []})
            topics = json.loads(content)
    except FileNotFoundError:
        return Result.success(data={"topics": []})
    except json.JSONDecodeError:
        return Result.success(data={"topics": []})

    connections.connect(host=milvus_settings.HOST, port=milvus_settings.PORT, alias="default")

    from app.milvus.service import get_collection

    output_fields = [
        "id", "content_id", "title", "text_preview", "raw_content", "chunk_index", "publish_time",
        "platform", "site_name", "author_name", "threat_category",
        "risk_level", "industry", "risk_score", "region", "url"
    ]

    all_topics_data = []
    total_items_all_topics = 0

    for topic_id_str, topic_data in topics.items():
        topic_id = int(topic_id_str)
        collection_name = f"topic_{topic_id_str}"

        print(f"[GET ALL TOPICS] Processing topic_id={topic_id}, collection={collection_name}")

        if not utility.has_collection(collection_name):
            print(f"[GET ALL TOPICS]   Collection does not exist, skipping")
            all_topics_data.append({
                "topic_id": topic_id,
                "topic_name": topic_data.get("name", ""),
                "collection_name": collection_name,
                "total_count": 0,
                "data": []
            })
            continue

        try:
            collection = get_collection(collection_name)
            collection.load()

            results = collection.query(
                expr="id >= 0",
                output_fields=output_fields,
                limit=10000,
                offset=0
            )

            print(f"[GET ALL TOPICS]   Found {len(results)} items")

            all_topics_data.append({
                "topic_id": topic_id,
                "topic_name": topic_data.get("name", ""),
                "collection_name": collection_name,
                "total_count": len(results),
                "data": results
            })
            total_items_all_topics += len(results)

        except Exception as e:
            print(f"[GET ALL TOPICS]   Error querying collection: {e}")
            all_topics_data.append({
                "topic_id": topic_id,
                "topic_name": topic_data.get("name", ""),
                "collection_name": collection_name,
                "total_count": 0,
                "error": str(e),
                "data": []
            })

    print(f"[GET ALL TOPICS] Complete! Total topics: {len(topics)}, Total items: {total_items_all_topics}")
    print(f"{'='*60}\n")

    return Result.success(data={
        "total_topics": len(topics),
        "total_items": total_items_all_topics,
        "topics": all_topics_data
    })


@router.get("/{topic_id}", response_model=Result[dict])
def get_topic_data(topic_id: int = PathParam(..., description="专题ID")):
    collection_name = f"topic_{topic_id}"

    connections.connect(host=milvus_settings.HOST, port=milvus_settings.PORT, alias="default")

    if not utility.has_collection(collection_name):
        raise HTTPException(status_code=404, detail=f"专题集合 '{collection_name}' 不存在")

    collection = get_collection(collection_name)
    collection.load()

    output_fields = [
        "id", "content_id", "title", "text_preview", "raw_content", "chunk_index", "publish_time",
        "platform", "site_name", "author_name", "threat_category",
        "risk_level", "industry", "risk_score", "region", "url"
    ]

    try:
        results = collection.query(
            expr="id >= 0",
            output_fields=output_fields,
            limit=10000,
            offset=0
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询专题集合失败: {str(e)}")

    topic_info = {
        "topic_id": topic_id,
        "collection_name": collection_name,
        "total_count": len(results),
        "data": results
    }

    return Result.success(data=topic_info)


@router.get("/{topic_id}/config", response_model=Result[dict])
def get_topic_config(topic_id: int = PathParam(..., description="专题ID")):
    print(f"\n{'='*60}")
    print(f"[GET TOPIC CONFIG] Getting config for topic_id={topic_id}")
    print(f"{'='*60}")

    try:
        with open(TOPICS_FILE, "r") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            content = f.read()
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            if not content.strip():
                raise HTTPException(status_code=404, detail="topics.json 为空")
            topics = json.loads(content)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="topics.json 文件不存在")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="topics.json 解析失败")

    topic_str_id = str(topic_id)
    if topic_str_id not in topics:
        raise HTTPException(status_code=404, detail=f"专题 {topic_id} 不存在")

    topic_data = topics[topic_str_id]

    print(f"[GET TOPIC CONFIG] Returning config for topic_id={topic_id}")
    print(f"{'='*60}\n")

    return Result.success(data={
        "topic_id": topic_id,
        "config": topic_data
    })


@router.patch("/{topic_id}/toggle", response_model=Result[dict])
def toggle_topic(topic_id: int = PathParam(..., description="专题ID")):
    print(f"\n{'='*60}")
    print(f"[TOGGLE TOPIC] Toggling topic_id={topic_id}")
    print(f"{'='*60}")

    try:
        with open(TOPICS_FILE, "r") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.seek(0)
                content = f.read()
                if content.strip():
                    topics = json.loads(content)
                    if not isinstance(topics, dict):
                        topics = {}
                else:
                    topics = {}
            except (json.JSONDecodeError, ValueError):
                topics = {}
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取 topics.json 失败: {str(e)}")

    topic_str_id = str(topic_id)
    if topic_str_id not in topics:
        raise HTTPException(status_code=404, detail=f"专题 {topic_id} 不存在")

    current_enabled = topics[topic_str_id].get("enabled", 1)
    new_enabled = 0 if current_enabled == 1 else 1
    action = "停用" if new_enabled == 0 else "启动"

    topics[topic_str_id]["enabled"] = new_enabled

    try:
        with open(TOPICS_FILE, "w") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            json.dump(topics, f, ensure_ascii=False, indent=2)
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        print(f"[TOGGLE TOPIC] Topic {topic_id} has been {'disabled' if new_enabled == 0 else 'enabled'}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"写入 topics.json 失败: {str(e)}")

    print(f"{'='*60}\n")

    return Result.success(data={
        "topic_id": topic_id,
        "enabled": new_enabled,
        "message": f"专题已{action}"
    })


@router.get("/sync/{topic_id}", response_model=Result[dict])
def sync_topic_incremental(topic_id: int = PathParam(..., description="专题ID")):
    print(f"\n{'='*60}")
    print(f"[INCREMENTAL SYNC] Starting incremental sync for topic_id={topic_id}")
    print(f"{'='*60}")

    try:
        with open(TOPICS_FILE, "r") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            content = f.read()
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            if not content.strip():
                raise HTTPException(status_code=404, detail="topics.json 为空")
            topics = json.loads(content)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="topics.json 文件不存在")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="topics.json 解析失败")

    topic_str_id = str(topic_id)
    if topic_str_id not in topics:
        raise HTTPException(status_code=404, detail=f"专题 {topic_id} 不存在")

    topic_data = topics[topic_str_id]

    if topic_data.get("enabled") == 0:
        raise HTTPException(status_code=400, detail=f"专题 {topic_id} 已停用，无法同步")

    cursor = topic_data.get("cursor", {})
    last_time = cursor.get("last_time", 0)
    last_id = cursor.get("last_id", "")

    print(f"[INCREMENTAL SYNC] Current cursor: last_time={last_time}, last_id={last_id}")

    if topic_data.get("mode") != "basic":
        raise HTTPException(status_code=400, detail="仅支持 basic 模式的增量同步")

    connections.connect(host=milvus_settings.HOST, port=milvus_settings.PORT, alias="default")

    from app.milvus.service import get_main_collection, create_topic_collection, check_topic_match

    main_collection = get_main_collection()
    if main_collection is None:
        raise HTTPException(status_code=500, detail="主集合不存在")

    topic_collection_name = f"topic_{topic_id}"
    if not utility.has_collection(topic_collection_name):
        print(f"[INCREMENTAL SYNC] Topic collection '{topic_collection_name}' does not exist, creating new one...")
        topic_collection = create_topic_collection(topic_str_id)
    else:
        from app.milvus.service import get_collection
        topic_collection = get_collection(topic_collection_name)
        topic_collection.load()

    output_fields = [
        "content_id", "title", "text_preview", "raw_content", "chunk_index", "publish_time",
        "platform", "site_name", "author_name", "threat_category",
        "risk_level", "industry", "risk_score", "region", "url"
    ]

    print(f"[INCREMENTAL SYNC] Querying main collection for items with publish_time > {last_time}...")

    all_new_items = []
    batch_size = 1000
    offset = 0
    total_scanned = 0
    total_matched = 0

    while True:
        try:
            results = main_collection.query(
                expr="publish_time > " + str(last_time),
                output_fields=output_fields,
                limit=batch_size,
                offset=offset
            )
        except Exception as e:
            print(f"[INCREMENTAL SYNC] Query error: {e}")
            break

        if not results:
            break

        for item in results:
            total_scanned += 1
            content_id = item.get("content_id", "")
            pub_time = item.get("publish_time", 0)

            if pub_time == last_time and content_id == last_id:
                print(f"[INCREMENTAL SYNC]   Skipping already synced item: content_id={content_id}")
                continue

            if check_topic_match(topic_data, item):
                total_matched += 1
                all_new_items.append(item)
                print(f"[INCREMENTAL SYNC]   ✓ MATCH: content_id={content_id}, "
                      f"threat={item.get('threat_category')}, "
                      f"level={item.get('risk_level')}, "
                      f"score={item.get('risk_score')}, "
                      f"pub_time={pub_time}")

        print(f"[INCREMENTAL SYNC] Processed batch at offset {offset}, scanned {total_scanned} items, matched {total_matched} so far...")
        offset += batch_size

    print(f"\n[INCREMENTAL SYNC] Scan complete: {total_scanned} scanned, {total_matched} matched")

    last_publish_time = last_time
    last_content_id = last_id

    if all_new_items:
        print(f"[INCREMENTAL SYNC] Inserting {len(all_new_items)} new items into topic collection...")

        entities = [
            [item.get("content_id", "") for item in all_new_items],
            [item.get("title", "") for item in all_new_items],
            [item.get("text_preview", "") for item in all_new_items],
            [item.get("raw_content", "") for item in all_new_items],
            [item.get("chunk_index", 0) for item in all_new_items],
            [[0.0] * milvus_settings.DIMENSION for _ in all_new_items],
            [item.get("publish_time", 0) for item in all_new_items],
            [item.get("platform", "") for item in all_new_items],
            [item.get("site_name", "") for item in all_new_items],
            [item.get("author_name", "") for item in all_new_items],
            [item.get("threat_category", "") for item in all_new_items],
            [item.get("risk_level", "") for item in all_new_items],
            [item.get("industry", "") for item in all_new_items],
            [item.get("risk_score", 0.0) for item in all_new_items],
            [item.get("region", "") for item in all_new_items],
            [item.get("url", "") for item in all_new_items],
        ]

        topic_collection.insert(entities)
        topic_collection.flush()
        print(f"[INCREMENTAL SYNC] Insert complete!")

        for item in all_new_items:
            pub_time = item.get("publish_time", 0)
            if pub_time > last_publish_time:
                last_publish_time = pub_time
                last_content_id = item.get("content_id", "")

    final_syn_time = datetime.now().isoformat()

    topics[topic_str_id]["cursor"] = {
        "last_time": last_publish_time,
        "last_id": last_content_id
    }
    topics[topic_str_id]["final_syn_time"] = final_syn_time

    try:
        with open(TOPICS_FILE, "w") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            json.dump(topics, f, ensure_ascii=False, indent=2)
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        print(f"[INCREMENTAL SYNC] Updated topics.json with new cursor")
    except Exception as e:
        print(f"[INCREMENTAL SYNC] Failed to update topics.json: {e}")

    print(f"[INCREMENTAL SYNC] Final cursor: last_publish_time={last_publish_time}, last_content_id={last_content_id}")
    print(f"[INCREMENTAL SYNC] Final sync time: {final_syn_time}")
    print(f"{'='*60}\n")

    return Result.success(data={
        "topic_id": topic_id,
        "scanned_count": total_scanned,
        "new_matched_count": total_matched,
        "last_publish_time": last_publish_time,
        "last_content_id": last_content_id,
        "final_syn_time": final_syn_time
    })