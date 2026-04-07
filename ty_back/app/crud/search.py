# app/crud/search.py
from app.utils.ch_client import get_ch_client
from typing import List, Dict, Any


def get_search_counts(keyword: str) -> List[Dict[str, Any]]:
    """获取各个 Tab 的统计数量"""
    client = get_ch_client()

    query = """
        SELECT 
            doc_type, 
            count(1) AS total_count
        FROM hawkeye.hawkeye_ads_search_unified_latest
        WHERE 
            event_date >= addYears(today(), -1) 
            AND normalized_text LIKE %(keyword)s
        GROUP BY doc_type
    """
    # 模糊查询需要我们在两边加上 %
    parameters = {"keyword": f"%{keyword}%"}

    result = client.query(query, parameters=parameters)

    # 将查询结果转换为字典列表
    counts = [{"doc_type": row[0], "total_count": row[1]} for row in result.result_rows]
    return counts


def get_search_results(keyword: str, doc_type: str = "All", limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
    """获取分页详情列表"""
    client = get_ch_client()

    query = """
        SELECT 
            doc_type, doc_id, toString(event_date) AS event_date, platform,
            title, text_preview, category_label, threat_category, 
            severity, primary_handle
        FROM hawkeye.hawkeye_ads_search_unified_latest
        WHERE 
            event_date >= addYears(today(), -1)
            AND normalized_text LIKE %(keyword)s
    """
    parameters = {"keyword": f"%{keyword}%", "limit": limit, "offset": offset}

    # 如果前端没有选“全部”，而是选了特定的 Tab
    if doc_type and doc_type != "All":
        query += " AND doc_type = %(doc_type)s"
        parameters["doc_type"] = doc_type

    query += " ORDER BY event_time DESC LIMIT %(limit)s OFFSET %(offset)s"

    result = client.query(query, parameters=parameters)

    # clickhouse-connect 提供了 column_names，方便我们将结果打包成字典
    columns = result.column_names
    items = [dict(zip(columns, row)) for row in result.result_rows]
    return items