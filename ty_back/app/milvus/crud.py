from app.utils.ch_client import execute_ch_query
from typing import List, Dict, Any, Optional


async def get_intel_content_list(
    content_id: Optional[str] = None,
    limit: int = 1000
) -> List[Dict[str, Any]]:
    if content_id:
        where_clause = f"WHERE c.content_id = '{content_id}'"
    else:
        where_clause = f"LIMIT {limit}"

    sql = f"""
    SELECT
        c.content_id,
        c.title,
        c.text_preview,
        cc.raw_content,
        c.publish_time,
        c.platform,
        c.site_name,
        c.author_name,
        c.threat_category,
        c.severity AS risk_level,
        c.industry,
        c.risk_score,
        c.region,
        c.url,
        c.topic,
        c.entity_tags
    FROM hawkeye_dwd_intel_content c
    LEFT JOIN hawkeye_dwd_intel_content_cold cc
        ON c.content_id = cc.content_id
    {where_clause}
    """

    result = await execute_ch_query(sql)
    return result.get("data", [])


async def get_intel_content_count(content_id: Optional[str] = None) -> int:
    if content_id:
        where_clause = f"WHERE content_id = '{content_id}'"
    else:
        where_clause = ""

    sql = f"""
    SELECT count() as cnt
    FROM hawkeye_dwd_intel_content
    {where_clause}
    """

    result = await execute_ch_query(sql)
    data = result.get("data", [])
    if data:
        return data[0].get("cnt", 0)
    return 0
