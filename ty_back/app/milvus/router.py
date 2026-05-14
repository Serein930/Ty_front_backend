from fastapi import APIRouter, Query
from typing import Optional
from app.milvus.crud import get_intel_content_list, get_intel_content_count
from app.milvus.service import insert_chunks, get_collection, create_ty_content_collection
from app.milvus.schemas import SyncRequest, SyncResponse
from app.schemas.base import Result
import time


router = APIRouter()


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list:
    if not text:
        return []
    chunks = []
    start = 0
    text_len = len(text)
    while start < text_len:
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks


async def sync_single_content(content_id: str, title: str, metadata: dict, raw_content: str) -> bool:
    try:
        if not raw_content:
            return False

        chunks = chunk_text(raw_content)
        if not chunks:
            return False

        insert_chunks(
            content_id=content_id,
            title=title,
            chunks=chunks,
            metadata=metadata
        )
        return True
    except Exception as e:
        print(f"Error syncing content_id {content_id}: {e}")
        return False


async def sync_content_to_milvus(
    content_id: Optional[str] = None,
    batch_size: int = 100,
    limit: int = 1000
) -> dict:
    start_time = time.time()

    total_count = await get_intel_content_count(content_id=content_id)
    content_list = await get_intel_content_list(content_id=content_id, limit=limit)

    print(f"[Sync] Start syncing {len(content_list)} items (total available: {total_count})")

    synced_count = 0
    for idx, item in enumerate(content_list):
        raw_content = item.get("raw_content", "")
        if not raw_content:
            print(f"[Sync] Skipping empty content_id: {item.get('content_id')}")
            continue

        metadata = {
            "publish_time": item.get("publish_time"),
            "platform": item.get("platform", "UNKNOWN"),
            "site_name": item.get("site_name", ""),
            "author_name": item.get("author_name", ""),
            "threat_category": item.get("threat_category", "UNKNOWN"),
            "risk_level": item.get("risk_level", "UNKNOWN"),
            "industry": item.get("industry", ""),
            "risk_score": item.get("risk_score", 0.0),
            "region": item.get("region", ""),
            "url": item.get("url", ""),
            "text_preview": item.get("text_preview", ""),
            "topic": item.get("topic", ""),
            "entity_tags": item.get("entity_tags", []),
        }

        success = await sync_single_content(
            content_id=item["content_id"],
            title=item.get("title", ""),
            metadata=metadata,
            raw_content=raw_content
        )
        if success:
            synced_count += 1
            print(f"[Sync] Progress: {idx + 1}/{len(content_list)} - synced content_id: {item['content_id']}")
        else:
            print(f"[Sync] Failed: {item['content_id']}")

    elapsed = time.time() - start_time
    print(f"[Sync] Completed! Synced {synced_count}/{len(content_list)} items in {elapsed:.2f}s")
    return {
        "synced_count": synced_count,
        "total_available": total_count,
        "elapsed_seconds": elapsed
    }


@router.get("/sync", response_model=Result[SyncResponse])
async def sync_milvus(
    content_id: Optional[str] = Query(None, description="指定内容ID同步，为空则同步全部"),
    batch_size: int = Query(100, description="批处理大小"),
    limit: int = Query(1000, description="最大同步条数")
):
    try:
        result = await sync_content_to_milvus(
            content_id=content_id,
            batch_size=batch_size,
            limit=limit
        )

        return Result.success(data=SyncResponse(
            synced_count=result["synced_count"],
            total_available=result["total_available"],
            message=f"同步完成，耗时 {result['elapsed_seconds']:.2f}秒"
        ))
    except Exception as e:
        return Result.error(code=500, msg=f"同步失败: {str(e)}")


@router.post("/sync", response_model=Result[SyncResponse])
async def sync_milvus_post(request: SyncRequest):
    try:
        result = await sync_content_to_milvus(
            content_id=request.content_id,
            batch_size=request.batch_size,
            limit=request.limit
        )

        return Result.success(data=SyncResponse(
            synced_count=result["synced_count"],
            total_available=result["total_available"],
            message=f"同步完成，耗时 {result['elapsed_seconds']:.2f}秒"
        ))
    except Exception as e:
        return Result.error(code=500, msg=f"同步失败: {str(e)}")


@router.post("/recreate", response_model=Result)
async def recreate_collection():
    try:
        collection = create_ty_content_collection()
        return Result.success(data={"collection": collection.name, "fields": len(collection.schema.fields)})
    except Exception as e:
        return Result.error(code=500, msg=f"重建集合失败: {str(e)}")


@router.get("/stats", response_model=Result)
async def get_stats():
    try:
        collection = get_collection()
        return Result.success(data={
            "collection_name": collection.name,
            "entities_count": collection.num_entities
        })
    except Exception as e:
        return Result.error(code=500, msg=f"获取统计失败: {str(e)}")
