# # app/utils/ch_client.py
# from clickhouse_driver import Client
# from app.config.config import ch_settings
#
#
# def get_ch_client():
#     """创建一个连接实例"""
#     return Client(
#         host=ch_settings.HOST,
#         port=ch_settings.PORT,
#         user=ch_settings.USER,
#         password=ch_settings.PASSWORD,
#         database=ch_settings.DATABASE
#     )
#
# # 实例化一个全局可用的 client
# ch_client = get_ch_client()


# app/utils/ch_client.py
import httpx
from httpx import HTTPStatusError
from app.config.config import ch_settings


async def execute_ch_query(query: str):
    """
    使用 HTTP 协议 (8123) 向 ClickHouse 发送查询
    """
    url = f"http://{ch_settings.HOST}:{ch_settings.PORT}/"

    is_write_query = any(q.strip().upper().startswith(("ALTER", "INSERT", "UPDATE", "DELETE")) for q in query.split(";"))

    params = {
        "query": query,
        "user": ch_settings.USER,
        "password": ch_settings.PASSWORD,
        "database": ch_settings.DATABASE,
    }
    if not is_write_query:
        params["default_format"] = "JSON"

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, params=params)
        if is_write_query:
            if response.status_code != 200:
                raise HTTPStatusError(
                    message=f"ClickHouse write error: {response.text}",
                    request=response.request,
                    response=response
                )
            content = response.text.strip()
            if content and "Exception" in content:
                raise Exception(f"ClickHouse query error: {content}")
            return {"success": True, "status_code": response.status_code}
        response.raise_for_status()
        content = response.text.strip()
        if not content:
            return {}
        try:
            return response.json()
        except Exception:
            return {}

# ... 原有代码保持不变 ...

async def get_case_content_by_ids(content_ids: list) -> dict:
    """
    根据 content_id 列表从 hawkeye_ads_case_content_latest 查询 title 和 text_preview
    返回 {content_id: {"title": ..., "text_preview": ...}}
    """
    if not content_ids:
        return {}

    ids_str = "','".join(content_ids)
    query = f"""
    SELECT content_id, title, text_preview
    FROM hawkeye.hawkeye_ads_case_content_latest
    WHERE content_id IN ('{ids_str}')
    """

    result = await execute_ch_query(query)
    data = result.get("data", [])

    return {item["content_id"]: {"title": item.get("title", ""), "text_preview": item.get("text_preview", "")} for item in data}


async def get_intel_list(limit: int = 10):
    """
    从 hawkeye_ads_search_unified_latest 查询数据
    并根据需求进行简单格式化
    """
    # 这里的 SQL 逻辑可以根据实际业务调整，比如增加 WHERE 过滤条件
    query = f"""
    SELECT 
        doc_id, 
        doc_type, 
        title, 
        text_preview, 
        severity, 
        region_province AS region, 
        topic, 
        event_date,
        dateDiff('day', event_date, today()) AS dayDiff,
        platform,
        primary_handle
    FROM hawkeye.hawkeye_ads_search_unified_latest
    ORDER BY event_time DESC
    LIMIT {limit}
    """
    return await execute_ch_query(query)


