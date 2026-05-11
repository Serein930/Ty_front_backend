from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Path as PathParam, Query

from app.schemas.alert import AlertListItem
from app.schemas.base import Result
from app.schemas.monitor import FollowAuthorReq, FollowStatusBatchReq
from app.services.monitor import author_follow_service
from app.utils.ch_client import execute_ch_query
from app.config.config import ch_settings

router = APIRouter(prefix="/api/monitor", tags=["关注管理"])

ALERT_TABLE_NAME = "hawkeye_test.hawkeye_ads_alert_event_latest"
ALERT_STATUS_TABLE_NAME = "hawkeye_test.hawkeye_dwd_alert_event_status"


async def get_db_client():
    return None


async def get_current_user():
    return {"tenant_id": "default", "user_id": "admin"}


def _escape_sql_string(s: str) -> str:
    return s.replace("'", "''")


def _parse_alert_items(data: list) -> List[AlertListItem]:
    from app.schemas.alert import AlertListItem
    items = []
    for row in data:
        items.append(
            AlertListItem(
                event_id=row.get("event_id", ""),
                rule_code=row.get("rule_code", ""),
                rule_name=row.get("rule_name", ""),
                title=row.get("title"),
                text_preview=row.get("text_preview"),
                author_name=row.get("author_name"),
                platform=row.get("platform"),
                site_name=row.get("site_name"),
                report_time=row.get("report_time"),
                severity=row.get("severity"),
                region=row.get("region"),
                topic=row.get("topic"),
                industry=row.get("industry"),
                read_status=row.get("read_status"),
                entity_tags=row.get("entity_tags", []),
                content_id=row.get("content_id"),
                false_positive=row.get("false_positive"),
                export_status=row.get("export_status"),
                search_title_text=row.get("search_title_text"),
                media_name=row.get("media_name"),
                threat_category=row.get("threat_category"),
                channel_id=row.get("channel_id"),
                source_handle=row.get("source_handle"),
                source_type=row.get("source_type"),
                entity_values_text=row.get("entity_values_text"),
                is_monitor_target=row.get("is_monitor_target"),
            )
        )
    return items


@router.get("/event", response_model=Result[list[AlertListItem]])
async def list_monitor_targets():
    data_query = f"""
    SELECT
        event_id, rule_code, rule_name, title, text_preview, author_name,
        platform, site_name, report_time, severity, region, topic, industry,
        read_status, entity_tags, content_id, false_positive, export_status,
        search_title_text, media_name, threat_category, channel_id,
        source_handle, source_type, entity_values_text, is_monitor_target
    FROM {ALERT_TABLE_NAME}
    WHERE is_monitor_target = 1 AND false_positive != 1
    ORDER BY report_time DESC
    """

    result = await execute_ch_query(data_query)
    items = _parse_alert_items(result.get("data", []))

    return Result.success(data=items, msg=f"共 {len(items)} 条")


@router.post("/{event_id}", response_model=Result[dict])
async def monitor_alert(
    event_id: str = PathParam(..., description="告警事件ID"),
    status: int = Query(..., description="关注状态，0=取消关注，1=关注"),
):
    check_query = f"""
    SELECT event_id FROM {ALERT_TABLE_NAME} WHERE event_id = '{_escape_sql_string(event_id)}'
    """
    check_result = await execute_ch_query(check_query)
    if not check_result.get("data", []):
        raise HTTPException(status_code=404, detail=f"告警事件 {event_id} 不存在")

    new_monitor_status = 1 if status == 0 else 0

    update_query = f"""
    ALTER TABLE {ALERT_TABLE_NAME} UPDATE is_monitor_target = {new_monitor_status}
    WHERE event_id = '{_escape_sql_string(event_id)}'
    """
    await execute_ch_query(update_query)

    status_update_query = f"""
    ALTER TABLE {ALERT_STATUS_TABLE_NAME} UPDATE is_monitor_target = {new_monitor_status}
    WHERE event_id = '{_escape_sql_string(event_id)}'
    """
    await execute_ch_query(status_update_query)

    return Result.success(data={"event_id": event_id, "is_monitor_target": new_monitor_status}, msg="关注状态已更新")


@router.post("/authors/follow")
async def follow_author(
    req: FollowAuthorReq,
    user: Annotated[dict, Depends(get_current_user)],
    client: Annotated[None, Depends(get_db_client)],
):
    tenant_id = user.get("tenant_id", "default")
    user_id = user.get("user_id", "admin")
    result = await author_follow_service.follow_author(tenant_id, user_id, req)
    return Result.success(data=result, msg="关注成功")


@router.post("/authors/unfollow")
async def unfollow_author(
    req: FollowAuthorReq,
    user: Annotated[dict, Depends(get_current_user)],
    client: Annotated[None, Depends(get_db_client)],
):
    tenant_id = user.get("tenant_id", "default")
    user_id = user.get("user_id", "admin")
    result = await author_follow_service.unfollow_author(tenant_id, user_id, req)
    return Result.success(data=result, msg="已取消关注")


@router.post("/authors/follow-status")
async def batch_get_follow_status(
    req: FollowStatusBatchReq,
    user: Annotated[dict, Depends(get_current_user)],
    client: Annotated[None, Depends(get_db_client)],
):
    tenant_id = user.get("tenant_id", "default")
    user_id = user.get("user_id", "admin")
    result = await author_follow_service.get_follow_status_batch(tenant_id, user_id, req.authors)
    return Result.success(data=result, msg="查询成功")


@router.get("/authors/following")
async def list_following_authors(
    user: Annotated[dict, Depends(get_current_user)],
    client: Annotated[None, Depends(get_db_client)],
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
):
    tenant_id = user.get("tenant_id", "default")
    user_id = user.get("user_id", "admin")
    result = await author_follow_service.list_following_authors(tenant_id, user_id, page, page_size)
    return Result.success(data=result, msg="查询成功")


@router.get("/authors/feed")
async def get_author_feed_list(
    user: Annotated[dict, Depends(get_current_user)],
    client: Annotated[None, Depends(get_db_client)],
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
):
    tenant_id = user.get("tenant_id", "default")
    user_id = user.get("user_id", "admin")
    result = await author_follow_service.get_author_feed_list(tenant_id, user_id, page, page_size)
    return Result.success(data=result, msg="查询成功")


@router.get("/authors/activity")
async def get_author_activity(
    user: Annotated[dict, Depends(get_current_user)],
    client: Annotated[None, Depends(get_db_client)],
    profile_id: str = Query(..., description="作者画像ID"),
):
    tenant_id = user.get("tenant_id", "default")
    user_id = user.get("user_id", "admin")
    result = await author_follow_service.get_author_activity(profile_id)
    return Result.success(data=result, msg="查询成功")