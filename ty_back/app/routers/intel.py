from fastapi import APIRouter, Query
from typing import List
from app.utils.ch_client import execute_ch_query
from app.schemas.base import Result
from app.schemas.intel import IntelItem

router = APIRouter()


@router.get("/intel/list", response_model=Result[List[IntelItem]])
async def get_intel_list(
        limit: int = Query(20, description="返回条数"),
        keyword: str = Query(None, description="搜索关键词")
):
    # 1. 构建搜索条件 (处理大小写敏感问题)
    where_clauses = ["A.doc_id != ''"]
    if keyword:
        # 强制小写匹配 A 表中的 materialized 字段
        k = keyword.lower()
        where_clauses.append(f"A.search_title_text LIKE '%{k}%'")

    where_str = " WHERE " + " AND ".join(where_clauses)

    # 2. SQL 逻辑 (增加 ifNull 处理 JOIN 为空的情况)
    sql = f"""
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
    FROM hawkeye.hawkeye_ads_search_unified_latest AS A
    LEFT JOIN (
        SELECT content_id, entity_tags, source_handle 
        FROM hawkeye.hawkeye_ads_case_content_latest
    ) AS B ON A.doc_id = B.content_id
    {where_str}
    ORDER BY A.event_time DESC
    LIMIT {limit}
    """

    try:
        # 3. 执行查询
        ch_res = await execute_ch_query(sql)
        items = ch_res.get("data", [])

        # 4. 返回统一的 Result 结构
        return Result.success(data=items)

    except Exception as e:
        # 5. 异常时返回 Result.error
        return Result.error(code=500, msg=f"数据库查询异常: {str(e)}")