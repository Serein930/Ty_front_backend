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
from app.config.config import ch_settings


async def execute_ch_query(query: str):
    """
    使用 HTTP 协议 (8123) 向 ClickHouse 发送查询
    """
    url = f"http://{ch_settings.HOST}:{ch_settings.PORT}/"

    # ClickHouse HTTP API 的标准参数格式
    params = {
        "query": query,
        "user": ch_settings.USER,
        "password": ch_settings.PASSWORD,
        "database": ch_settings.DATABASE,
        "default_format": "JSON"  # 告诉 ClickHouse 直接返回 JSON 格式，方便处理
    }

    # 使用 httpx 发起异步 POST 请求
    async with httpx.AsyncClient() as client:
        response = await client.post(url, params=params, timeout=10.0)
        # 如果 HTTP 状态码不是 200，主动抛出异常
        response.raise_for_status()
        return response.json()

# ... 原有代码保持不变 ...

async def get_case_content_by_ids(content_ids: list) -> dict:
    """
    根据 content_id 列表从 hawkeye_ads_case_content_latest_test 查询 title 和 text_preview
    返回 {content_id: {"title": ..., "text_preview": ...}}
    """
    if not content_ids:
        return {}

    ids_str = "','".join(content_ids)
    query = f"""
    SELECT content_id, title, text_preview
    FROM hawkeye.hawkeye_ads_case_content_latest_test
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


