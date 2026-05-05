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


@router.post("/search/stream")
async def rag_search_stream(request: RAGSearchRequest):
    """
    RAG 智能搜索流式接口

    使用 Server-Sent Events (SSE) 流式返回：
    1. 思考过程（reasoning）
    2. 最终答案

    事件格式：
    - event: thinking | answer | done | error
    - data: JSON 字符串
    """
    from fastapi.responses import StreamingResponse
    import json

    async def event_generator():
        import json
        logger.info(f"[stream] 开始处理请求, session_id: {request.session_id}, question: {request.question}")
        try:
            rag_search_service._ensure_session_loaded(request.session_id)
            logger.info(f"[stream] 会话已加载")

            rewritten_question = rag_search_service._rewrite_question(
                request.question, request.session_id
            )
            logger.info(f"[stream] 改写后的问题: {rewritten_question}")
            yield f"event: rewritten\ndata: {json.dumps({'question': rewritten_question})}\n\n"

            logger.info(f"[stream] 开始检索内容...")
            all_results = rag_search_service._search_content(rewritten_question)
            logger.info(f"[stream] 检索完成，结果数量: {len(all_results)}")
            
            if request.use_rerank and rag_search_service.reranker:
                all_results = rag_search_service._rerank_results(request.question, all_results)
                logger.info(f"[stream] Rerank 后结果数量: {len(all_results)}")
            
            all_results = all_results[:20]
            logger.info(f"[stream] 最终返回结果数量: {len(all_results)}")

            yield f"event: sources\ndata: {json.dumps({'sources': all_results})}\n\n"

            full_answer = []
            thinking_content = []
            think_phase = False
            answer_phase = False
            logger.info(f"[stream] 🔄 开始流式生成答案...")
            async for chunk in rag_search_service.generate_answer_stream(
                question=request.question,
                context=all_results,
                session_id=request.session_id
            ):
                event_type = chunk.get("event", "answer")
                content = chunk.get("content", "")

                if event_type == "done":
                    logger.info(f"[stream] 收到流结束信号")
                    continue

                if event_type == "error":
                    logger.error(f"[stream] 收到错误事件: {content}")
                    yield f"event: error\ndata: {json.dumps({'message': content})}\n\n"
                    return

                logger.debug(f"[stream] 收到事件: {event_type}, content长度: {len(content)}")

                if event_type == "thinking" and content:
                    if not think_phase:
                        logger.info(f"[stream] 🧠 ===== 阶段1: 开始流式输出思考过程 (SSE) =====")
                        think_phase = True
                    thinking_content.append(content)
                    yield f"event: thinking\ndata: {json.dumps({'content': content})}\n\n"
                elif event_type == "answer" and content:
                    if not answer_phase:
                        if think_phase:
                            logger.info(f"[stream] ✅ 思考过程全部输出完毕 (共 {len(''.join(thinking_content))} 字符)")
                        logger.info(f"[stream] 📝 ===== 阶段2: 开始流式输出最终答案 (SSE) =====")
                        answer_phase = True
                    full_answer.append(content)
                    yield f"event: answer\ndata: {json.dumps({'content': content})}\n\n"

            final_answer = "".join(full_answer)
            final_thinking = "".join(thinking_content)
            logger.info(f"[stream] 📊 ===== 流式输出统计 =====")
            logger.info(f"[stream]   思考过程: {len(final_thinking)} 字符")
            logger.info(f"[stream]   最终答案: {len(final_answer)} 字符")
            if final_thinking:
                logger.info(f"[stream] 完整思考过程:\n{final_thinking}")
            if final_answer:
                logger.info(f"[stream] 完整最终输出:\n{final_answer}")

            # Always send the done event after the generator completes
            yield f"event: done\ndata: {json.dumps({'model': rag_search_service.llm_generator.model_name})}\n\n"

            rag_search_service._manage_history(request.session_id, request.question, final_answer)
            logger.info(f"[stream] 历史已保存")
            logger.info(f"[stream] 流式响应完成")

        except Exception as e:
            logger.error(f"[stream] 流式搜索失败: {e}", exc_info=True)
            yield f"event: error\ndata: {json.dumps({'message': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


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
