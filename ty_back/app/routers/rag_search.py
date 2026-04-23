"""
RAG Search Router 模块
====================

该模块定义了 RAG 搜索功能的 FastAPI 路由层。

主要接口：
- POST /api/rag/search - RAG 智能搜索
- GET /api/rag/history/{session_id} - 获取对话历史
- DELETE /api/rag/history/{session_id} - 清除对话历史
- POST /api/rag/rewrite - 查询改写

路由前缀：/api/rag
标签：["RAG 搜索"]

请求处理流程：
1. 接收并验证请求参数
2. 调用 RAGSearchService 执行搜索
3. 格式化响应并返回
"""

import collections
from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.schemas.rag_search import (
    RAGSearchRequest,
    RAGSearchResponse,
    RAGHistoryResponse,
    RAGRewriteRequest,
    RAGRewriteResponse,
    RAGClearHistoryRequest,
    HistoryMessage
)
from app.services.rag_search_service import rag_search_service

import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/rag", tags=["RAG 搜索"])


@router.post("/search", response_model=RAGSearchResponse)
async def rag_search(request: RAGSearchRequest):
    """
    RAG 智能搜索接口

    执行完整的 RAG 搜索流程：
    1. 查询改写（结合对话历史）
    2. 检索 ty_content 集合
    3. Rerank 重排序（可选）
    4. 生成结构化回答

    Args:
        request: RAGSearchRequest
            - question: 用户问题
            - session_id: 会话 ID
            - use_rerank: 是否使用重排序

    Returns:
        RAGSearchResponse
            - answer: AI 生成的答案
            - sources: 参考来源列表
            - session_id: 会话 ID
            - model: 使用的模型名称
    """
    try:
        logger.info(f"=" * 60)
        logger.info(f"收到 RAG 搜索请求:")
        logger.info(f"  - question: {request.question}")
        logger.info(f"  - session_id: {request.session_id}")
        logger.info(f"  - use_rerank: {request.use_rerank}")
        
        result = rag_search_service.search(
            question=request.question,
            session_id=request.session_id,
            use_rerank=request.use_rerank
        )
        
        logger.info(f"RAG 搜索响应:")
        logger.info(f"  - status: 200 OK")
        logger.info(f"  - answer 长度: {len(result.get('answer', ''))} 字符")
        logger.info(f"  - sources 数量: {len(result.get('sources', []))}")
        logger.info(f"  - model: {result.get('model')}")
        logger.info(f"=" * 60)
        
        return RAGSearchResponse(**result)
    except Exception as e:
        logger.error(f"RAG 搜索失败: {e}")
        raise HTTPException(status_code=500, detail=f"RAG 搜索失败: {str(e)}")


@router.get("/history/{session_id}", response_model=RAGHistoryResponse)
async def get_rag_history(session_id: str):
    """
    获取 RAG 对话历史

    Args:
        session_id: 会话 ID（路径参数）

    Returns:
        RAGHistoryResponse
            - session_id: 会话 ID
            - name: 会话名称
            - summary: 历史摘要
            - history: 消息历史列表
    """
    try:
        history_data = rag_search_service.get_history(session_id)

        history_messages = [
            HistoryMessage(
                type=item.get("type", ""),
                content=item.get("content", ""),
                time=item.get("time")
            )
            for item in history_data.get("history", [])
        ]

        return RAGHistoryResponse(
            session_id=history_data["session_id"],
            name=history_data["name"],
            summary=history_data["summary"],
            history=history_messages
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取历史失败: {str(e)}")


@router.delete("/history/{session_id}")
async def clear_rag_history(session_id: str):
    """
    清除 RAG 对话历史

    Args:
        session_id: 会话 ID（路径参数）

    Returns:
        {"message": "历史已清除", "session_id": "xxx"}
    """
    try:
        rag_search_service.clear_history(session_id)
        return {"message": "历史已清除", "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清除历史失败: {str(e)}")


@router.post("/rewrite", response_model=RAGRewriteResponse)
async def rewrite_question(request: RAGRewriteRequest):
    """
    查询改写接口

    根据对话历史将用户问题改写为包含完整上下文的查询语句

    Args:
        request: RAGRewriteRequest
            - question: 原始问题
            - session_id: 会话 ID

    Returns:
        RAGRewriteResponse
            - rewritten_question: 改写后的查询
            - session_id: 会话 ID
    """
    try:
        rewritten = rag_search_service._rewrite_question(
            question=request.question,
            session_id=request.session_id
        )
        return RAGRewriteResponse(
            rewritten_question=rewritten,
            session_id=request.session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询改写失败: {str(e)}")


@router.get("/sessions")
async def list_sessions():
    """
    列出所有会话

    返回当前内存中加载的所有会话 ID 列表

    Returns:
        {"sessions": ["session_id_1", "session_id_2", ...]}
    """
    sessions = list(rag_search_service.sessions.keys())
    return {"sessions": sessions, "count": len(sessions)}


@router.get("/stats")
async def get_stats():
    """
    获取 RAG 服务统计信息

    返回当前服务状态和配置信息

    Returns:
        服务统计信息字典
    """
    from app.config.config import milvus_settings, rerank_settings

    return {
        "status": "running",
        "collections": {
            "ty_content": milvus_settings.COLLECTION_NAME,
        },
        "rerank_enabled": rerank_settings.USE_RERANK,
        "active_sessions": len(rag_search_service.sessions),
        "milvus_host": milvus_settings.HOST,
        "milvus_port": milvus_settings.PORT,
        "active_sessions": len(rag_search_service.sessions)
    }
