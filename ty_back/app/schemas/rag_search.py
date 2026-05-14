"""
RAG Search Schema 模块
=====================

该模块定义了 RAG 搜索功能的请求和响应数据结构（Pydantic 模型）。

主要模型：
- RAGSearchRequest: RAG 搜索请求
- RAGSearchResponse: RAG 搜索响应
- RAGHistoryResponse: RAG 历史记录响应
- RAGRewriteRequest: 查询改写请求
- RAGRewriteResponse: 查询改写响应

使用场景：
- FastAPI 路由层与前端的数据交互
- 请求参数验证和响应数据序列化
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class RAGSearchRequest(BaseModel):
    """
    RAG 智能搜索请求

    用于向 RAG 系统发起一次完整的搜索对话请求。

    Attributes:
        question: 用户问题，必填
        session_id: 会话 ID，用于关联对话历史
        use_rerank: 是否使用重排序模型进行结果优化
    """

    question: str = Field(..., description="用户问题", min_length=1)
    session_id: str = Field(..., description="会话 ID，用于关联对话历史")
    use_rerank: bool = Field(default=True, description="是否使用重排序")


class SearchSource(BaseModel):
    """
    搜索结果来源信息

    描述单条参考来源的详细信息

    Attributes:
        content_id: 内容唯一标识
        title: 内容标题
        text_preview: 内容摘要
        raw_content: 原始内容
        platform: 来源平台
        site_name: 网站名称
        author_name: 作者/发布者
        threat_category: 威胁类别
        risk_level: 风险等级
        industry: 行业
        risk_score: 风险分数
        region: 地区
        publish_time: 发布时间
        url: 原文链接
        topic: 主题
        entity_tags: 实体标签简表
    """

    content_id: str = Field(..., description="内容唯一标识")
    title: str = Field(..., description="内容标题")
    text_preview: str = Field(..., description="内容摘要")
    raw_content: Optional[str] = Field(None, description="原始内容")
    platform: Optional[str] = Field(None, description="来源平台")
    site_name: Optional[str] = Field(None, description="网站名称")
    author_name: Optional[str] = Field(None, description="作者/发布者")
    threat_category: Optional[str] = Field(None, description="威胁类别")
    risk_level: Optional[str] = Field(None, description="风险等级: 高危/中危/低危")
    industry: Optional[str] = Field(None, description="行业")
    risk_score: Optional[float] = Field(None, description="风险分数")
    region: Optional[str] = Field(None, description="地区")
    publish_time: Optional[int] = Field(None, description="发布时间戳")
    url: Optional[str] = Field(None, description="原文链接")
    topic: Optional[str] = Field(None, description="主题")
    entity_tags: Optional[List[str]] = Field(None, description="实体标签简表")


class RAGSearchResponse(BaseModel):
    """
    RAG 智能搜索响应

    返回 RAG 系统生成的答案及相关参考来源

    Attributes:
        answer: AI 生成的答案
        sources: 参考来源列表
        session_id: 关联的会话 ID
        model: 使用的模型名称
    """

    answer: str = Field(..., description="AI 生成的答案")
    sources: List[Dict[str, Any]] = Field(default_factory=list, description="参考来源列表")
    session_id: str = Field(..., description="关联的会话 ID")
    model: str = Field(..., description="使用的模型名称")


class HistoryMessage(BaseModel):
    """
    历史消息记录

    单条对话历史消息

    Attributes:
        type: 消息类型 (human/ai)
        content: 消息内容
        time: 发送时间
    """

    type: str = Field(..., description="消息类型: human/ai")
    content: str = Field(..., description="消息内容")
    time: Optional[str] = Field(None, description="发送时间")


class RAGHistoryResponse(BaseModel):
    """
    RAG 历史记录响应

    返回指定会话的所有对话历史

    Attributes:
        session_id: 会话 ID
        name: 会话名称
        summary: 历史摘要
        history: 消息历史列表
    """

    session_id: str = Field(..., description="会话 ID")
    name: str = Field(..., description="会话名称")
    summary: str = Field(default="", description="历史摘要")
    history: List[HistoryMessage] = Field(default_factory=list, description="消息历史列表")


class RAGRewriteRequest(BaseModel):
    """
    查询改写请求

    请求 LLM 根据对话历史改写用户问题

    Attributes:
        question: 原始用户问题
        session_id: 会话 ID
    """

    question: str = Field(..., description="原始用户问题")
    session_id: str = Field(..., description="会话 ID")


class RAGRewriteResponse(BaseModel):
    """
    查询改写响应

    返回改写后的查询语句

    Attributes:
        rewritten_question: 改写后的查询语句
        session_id: 会话 ID
    """

    rewritten_question: str = Field(..., description="改写后的查询语句")
    session_id: str = Field(..., description="会话 ID")


class RAGClearHistoryRequest(BaseModel):
    """
    清除历史记录请求

    Attributes:
        session_id: 要清除的会话 ID
    """

    session_id: str = Field(..., description="会话 ID")
