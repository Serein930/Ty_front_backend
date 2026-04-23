from typing import Any, Dict, List

import httpx

from app.config.config import ch_settings


def _escape_like(value: str) -> str:
    # Minimal escaping to avoid malformed SQL in demo mode.
    return value.replace("'", "''")


def _execute_ch_sql(query: str) -> Dict[str, Any]:
    url = f"http://{ch_settings.HOST}:{ch_settings.PORT}/"
    params = {
        "query": query,
        "user": ch_settings.USER,
        "password": ch_settings.PASSWORD,
        "database": ch_settings.DATABASE,
        "default_format": "JSON",
    }
    with httpx.Client(timeout=12.0) as client:
        response = client.post(url, params=params)
        response.raise_for_status()
        return response.json()


def get_search_counts(keyword: str) -> List[Dict[str, Any]]:
    """获取各个 Tab 的统计数量"""
    kw = _escape_like(keyword.lower())

    query = f"""
        SELECT 
            doc_type, 
            count(1) AS total_count
        FROM hawkeye_test.hawkeye_ads_search_unified_latest
        WHERE 
            doc_id != '' 
            AND text_preview LIKE '%{kw}%'
        GROUP BY doc_type
    """

    result = _execute_ch_sql(query)
    print(f"[DEBUG] get_search_counts SQL: {query}")  # 添加调试日志
    rows = result.get("data", [])
    counts = [
        {"doc_type": row.get("doc_type", "unknown"), "total_count": int(row.get("total_count", 0))}
        for row in rows
    ]
    return counts


def get_search_results(keyword: str, doc_type: str = "All", limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
    """获取分页详情列表"""
    kw = _escape_like(keyword.lower())

    where_clauses = ["A.doc_id != ''", f"(A.text_preview LIKE '%{kw}%' OR ifNull(A.text_preview, '') LIKE '%{kw}%')"]
    if doc_type and doc_type != "All":
        where_clauses.append(f"A.doc_type = '{_escape_like(doc_type)}'")

    where_str = " WHERE " + " AND ".join(where_clauses)

    query = f"""
        SELECT 
            A.doc_id AS id,
            A.doc_type AS viewType,
            A.title AS title,
            A.text_preview AS summary,
            A.severity AS risk,
            A.platform AS media,
            A.region_province AS region,
            A.topic AS topic,
            toString(A.event_date) AS date,
            dateDiff('day', A.event_date, today()) AS dayDiff,
            arrayDistinct(arrayConcat(ifNull(B.entity_tags, []), [A.topic, A.platform])) AS entities,
            arrayFilter(x -> x != '', [A.primary_handle, ifNull(B.source_handle, '')]) AS relatedAccounts
        FROM hawkeye_test.hawkeye_ads_search_unified_latest AS A
        LEFT JOIN (
            SELECT content_id, entity_tags, source_handle 
            FROM hawkeye_test.hawkeye_ads_case_content_latest
        ) AS B ON A.doc_id = B.content_id
        {where_str}
        ORDER BY A.event_time DESC
        LIMIT {int(limit)} OFFSET {int(offset)}
    """
    
    print(f"[DEBUG] SQL Query: {query}")  # 添加调试日志

    result = _execute_ch_sql(query)
    print(f"[DEBUG] Result rows count: {len(result.get('data', []))}")  # 添加调试日志
    items = result.get("data", [])
    return items