import time
from typing import List, Dict, Any
from app.schemas.monitor import FollowAuthorReq
from app.utils.ch_client import execute_ch_query


TABLE_NAME = "hawkeye_test.hawkeye_user_follow_author"


async def upsert_follow_state(
    client, tenant_id: str, user_id: str, req: FollowAuthorReq, is_followed: int
) -> Dict[str, Any]:
    """
    写入或更新关注状态。
    通过 INSERT 一条新数据实现状态变更，ReplacingMergeTree 引擎会根据 ORDER BY
    (tenant_id, user_id, target_id) 结合 version 字段自动去重，保留最新版本。
    """
    target_id = req.target_id
    update_time_ms = int(time.time() * 1000)
    update_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(update_time_ms / 1000))
    query = f"""
        INSERT INTO {TABLE_NAME} (
            tenant_id, user_id, target_id, profile_id, platform,
            source_handle_norm, author_name, avatar_url,
            is_followed, update_time, version
        ) VALUES (
            '{tenant_id}', '{user_id}', '{target_id}', '{req.profile_id or ''}',
            '{req.platform}', '{req.source_handle_norm}', '{req.author_name or ''}',
            '{req.avatar_url or ''}', {is_followed}, '{update_time}', {update_time_ms}
        )
    """
    return await execute_ch_query(query)


async def get_following_authors(
    client, tenant_id: str, user_id: str, limit: int, offset: int
) -> Dict[str, Any]:
    """
    分页查询当前用户已关注的所有作者列表。
    使用 FINAL 关键字确保查询时触发 ReplacingMergeTree 的去重逻辑。
    """
    query = f"""
        SELECT
            target_id, profile_id, platform, source_handle_norm,
            author_name, avatar_url, is_followed, update_time
        FROM {TABLE_NAME} FINAL
        WHERE tenant_id = '{tenant_id}'
          AND user_id = '{user_id}'
          AND is_followed = 1
        ORDER BY update_time DESC
        LIMIT {limit} OFFSET {offset}
    """
    return await execute_ch_query(query)


async def batch_get_follow_status(
    client, tenant_id: str, user_id: str, target_ids: List[str]
) -> Dict[str, bool]:
    """
    批量查询指定作者的关注状态。
    返回 Dict[target_id, is_followed]（True=已关注，False=未关注）。
    """
    if not target_ids:
        return {}

    ids_placeholder = "','".join(target_ids)
    query = f"""
        SELECT target_id, is_followed
        FROM {TABLE_NAME} FINAL
        WHERE tenant_id = '{tenant_id}'
          AND user_id = '{user_id}'
          AND target_id IN ('{ids_placeholder}')
    """
    result = await execute_ch_query(query)
    rows = result.get("data", [])

    status_map: Dict[str, bool] = {}
    for row in rows:
        target_id = row.get("target_id", "")
        is_followed = row.get("is_followed", 0)
        status_map[target_id] = is_followed == 1

    for tid in target_ids:
        if tid not in status_map:
            status_map[tid] = False

    return status_map


async def get_author_feed(
    client, tenant_id: str, user_id: str, limit: int, offset: int
) -> Dict[str, Any]:
    """
    查询被关注作者的最新动态（Feed 流）。
    通过子查询找到当前用户已关注的作者 profile_id，
    再从 hawkeye_ads_case_content_latest 表中拉取这些作者的最新内容。
    """
    query = f"""
        SELECT c.*
        FROM hawkeye_test.hawkeye_ads_case_content_latest c
        WHERE c.profile_id IN (
            SELECT profile_id
            FROM {TABLE_NAME} FINAL
            WHERE tenant_id = '{tenant_id}'
              AND user_id = '{user_id}'
              AND is_followed = 1
              AND profile_id != ''
        )
        ORDER BY c.publish_time DESC
        LIMIT {limit} OFFSET {offset}
    """
    return await execute_ch_query(query)


async def get_author_activity_stat(
    client, profile_id: str
) -> Dict[str, Any]:
    """
    统计指定作者（profile_id）在全网发布的活跃时段分布。
    按"星期几"（周一~周日）和"小时"（0~23）进行二级分组计数。
    """
    query = f"""
        SELECT
            dayOfWeek(toDateTime(publish_time)) - 1 AS day_index,
            toHour(toDateTime(publish_time)) AS hour,
            count() AS cnt
        FROM hawkeye_test.hawkeye_ads_case_content_latest
        WHERE profile_id = '{profile_id}'
          AND publish_time IS NOT NULL
          AND publish_time != 0
        GROUP BY day_index, hour
        ORDER BY day_index, hour
    """
    return await execute_ch_query(query)
