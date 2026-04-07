# app/routers/search.py
from fastapi import APIRouter, Query
from app.crud import search as crud_search
from app.schemas.search import SearchResponse

router = APIRouter(prefix="/api/search", tags=["全局检索"])


@router.get("/unified", response_model=SearchResponse)
def unified_search(
        keyword: str = Query(..., description="搜索关键词"),
        doc_type: str = Query("All", description="数据类型: All, intel, person, account"),
        page: int = Query(1, ge=1, description="页码"),
        size: int = Query(20, ge=1, le=100, description="每页数量")
):
    offset = (page - 1) * size

    # 1. 查询各分类数量
    tabs_count = crud_search.get_search_counts(keyword)

    # 2. 查询当前页的详细列表
    items = crud_search.get_search_results(
        keyword=keyword,
        doc_type=doc_type,
        limit=size,
        offset=offset
    )

    return SearchResponse(
        tabs=tabs_count,
        items=items
    )