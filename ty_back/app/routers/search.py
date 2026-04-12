# app/routers/search.py
from time import perf_counter
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.crud import search as crud_search
from app.schemas.search import SearchResponse
from app.services.llm_service import generate_ai_summary

router = APIRouter(prefix="/api/search", tags=["全局检索"])


class AISummaryRequest(BaseModel):
    keyword: str = Field(default="", description="搜索关键词")
    doc_type: str = Field(default="All", description="数据类型: All, intel, person, account")
    max_items: int = Field(default=8, ge=1, le=30, description="用于构建上下文的最大样本数")
    filters: Dict[str, Any] = Field(default_factory=dict, description="前端筛选信息")


class AISummaryResponse(BaseModel):
    summary: str
    references: List[Dict[str, Any]]
    model: str
    elapsed_ms: int
    mock_used: bool
    error: Optional[str] = ""


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


@router.post("/ai-summary", response_model=AISummaryResponse)
def ai_summary(payload: AISummaryRequest):
    started = perf_counter()
    keyword = (payload.keyword or "").strip()
    doc_type = payload.doc_type or "All"
    max_items = payload.max_items

    refs: List[Dict[str, Any]] = []
    try:
        query_keyword = keyword if keyword else " "
        raw_items = crud_search.get_search_results(
            keyword=query_keyword,
            doc_type=doc_type,
            limit=max_items,
            offset=0,
        )
        refs = [
            {
                "doc_id": item.get("doc_id", ""),
                "doc_type": item.get("doc_type", ""),
                "title": item.get("title", ""),
                "severity": item.get("severity", ""),
                "platform": item.get("platform", ""),
                "event_date": item.get("event_date", ""),
            }
            for item in raw_items[:max_items]
        ]
    except Exception:
        refs = []

    prompt_lines = [
        "请基于以下检索上下文输出研判摘要，要求中文，分点，包含风险建议。",
        f"关键词: {keyword or '（空关键词）'}",
        f"类型过滤: {doc_type}",
        f"筛选器: {payload.filters}",
        f"参考样本数量: {len(refs)}",
        "参考样本:",
    ]
    for idx, ref in enumerate(refs, start=1):
        prompt_lines.append(
            f"{idx}. [{ref.get('doc_type', '-')}/{ref.get('severity', '-')}] {ref.get('title', '')}"
            f" | 平台:{ref.get('platform', '-')}, 日期:{ref.get('event_date', '-')}, ID:{ref.get('doc_id', '-') }"
        )

    llm_result = generate_ai_summary("\n".join(prompt_lines))
    elapsed_ms = int((perf_counter() - started) * 1000)

    return AISummaryResponse(
        summary=llm_result.get("summary", ""),
        references=refs,
        model=llm_result.get("model", ""),
        elapsed_ms=max(elapsed_ms, llm_result.get("elapsed_ms", 0)),
        mock_used=bool(llm_result.get("mock_used", False)),
        error=llm_result.get("error", ""),
    )