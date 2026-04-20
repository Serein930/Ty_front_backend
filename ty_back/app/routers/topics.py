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

router = APIRouter(prefix="/api/topics", tags=["专题管理"])

TOPICS_FILE = Path(__file__).resolve().parent.parent / "config" / "topics.json"


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

    for field in ["last_saved_draft_at", "applied_at", "deleted_at"]:
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