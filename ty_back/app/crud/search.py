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
    kw = _escape_like(keyword)

    query = f"""
        SELECT 
            doc_type, 
            count(1) AS total_count
        FROM hawkeye.hawkeye_ads_search_unified_latest
        WHERE 
            event_date >= addYears(today(), -1) 
            AND normalized_text LIKE '%{kw}%'
        GROUP BY doc_type
    """

    result = _execute_ch_sql(query)
    rows = result.get("data", [])
    counts = [
        {"doc_type": row.get("doc_type", "unknown"), "total_count": int(row.get("total_count", 0))}
        for row in rows
    ]
    return counts


def get_search_results(keyword: str, doc_type: str = "All", limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
    """获取分页详情列表"""
    kw = _escape_like(keyword)

    query = f"""
        SELECT 
            doc_type, doc_id, toString(event_date) AS event_date, platform,
            title, text_preview, category_label, threat_category, 
            severity, primary_handle
        FROM hawkeye.hawkeye_ads_search_unified_latest
        WHERE 
            event_date >= addYears(today(), -1)
            AND normalized_text LIKE '%{kw}%'
    """

    # 如果前端没有选“全部”，而是选了特定的 Tab
    if doc_type and doc_type != "All":
        query += f" AND doc_type = '{_escape_like(doc_type)}'"

    query += f" ORDER BY event_time DESC LIMIT {int(limit)} OFFSET {int(offset)}"

    result = _execute_ch_sql(query)
    items = result.get("data", [])
    return items