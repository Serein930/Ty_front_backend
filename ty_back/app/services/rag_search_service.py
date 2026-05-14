"""
RAG Search Service 模块
=====================

该模块是 RAG 搜索功能的核心服务层，封装了所有 RAG 相关的业务逻辑。

主要功能：
- 初始化 LLM、Reranker、Milvus 连接
- 维护对话历史和会话管理
- 执行向量检索（ty_content 集合）
- 查询改写和上下文补全
- Rerank 重排序
- 生成最终回答

设计原则：
- 单例模式：全局共享 RAGSearchService 实例
- 懒加载：按需初始化各组件
"""

import os
import json
import math
import time
import logging
from typing import List, Dict, Any, Optional, AsyncGenerator
from concurrent.futures import ThreadPoolExecutor

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage

from pymilvus import connections, Collection, utility

from app.config.config import milvus_settings, rerank_settings, llm_settings

logger = logging.getLogger(__name__)


class StreamTagParser:
    """
    流式标签解析器

    从流式内容中解析 <think>...</think> 标签及其 Markdown 变体。
    处理流式传输中的标签截断问题（如 <thi + nk> 分两次到达）。

    支持格式：
    1. <think>...</think> XML 标签
    2. ### 思考过程 ... ### 最终回答 Markdown 格式
    3. ### 思考过程 ... --- 分隔线格式

    兜底策略：
    - 前 50 字符内无任何开始标签 → 全部视为 answer_content
    - 流结束标签未闭合 → 自动闭合，已接收内容全部视为 think_content
    """

    # 开始标签模式（按匹配优先级排序）
    START_PATTERNS = [
        ("think_xml", "<think>"),
        ("md_think", "### 思考过程"),
    ]

    # 结束标签模式
    END_PATTERNS = [
        ("think_xml_end", "</think>"),
        ("md_answer", "### 最终回答"),
        ("sep_line", "\n---\n"),
        ("sep_line_start", "\n---"),
    ]

    # 残留标签清理正则
    CLEANUP_RESIDUAL = [
        (r'</?think>', ''),
        (r'###\s*最终回答\s*', ''),
        (r'###\s*思考过程\s*', ''),
    ]

    # 标签截断候选前缀（用于保留缓冲区尾部）
    TRUNCATION_CANDIDATES = [
        "<", "<t", "<th", "<thi", "<thin", "<think", "<think>",
        "</", "</t", "</th", "</thi", "</thin", "</think", "</think>",
        "#", "##", "###", "### ", "### 思", "### 思考", "### 思考过", "### 思考过程",
        "### 最", "### 最终", "### 最终回", "### 最终回答",
        "\n", "\n-", "\n--", "\n---", "\n---\n",
    ]
    MAX_TRUNCATION_LEN = max(len(c) for c in TRUNCATION_CANDIDATES)

    def __init__(self):
        self._buffer = ""            # 待解析的内容缓冲区
        self._state = "detecting"    # detecting | thinking | answering
        self._total_received = ""    # 全部已接收内容（用于前50字符检测）
        self._first_chunk_checked = False
        self._no_tag_mode = False    # 降级模式：前50字符无标签

    def feed(self, chunk: str) -> list:
        """
        处理一个内容块，返回解析出的事件列表。
        每个事件为 {"event": "thinking"|"answer", "content": str}
        """
        events = []
        self._total_received += chunk

        # 前 50 字符检测：无任何开始标签则降级为全 answer 模式
        if not self._first_chunk_checked and len(self._total_received) >= 50:
            self._first_chunk_checked = True
            if not self._has_any_start_tag(self._total_received[:60]):
                self._no_tag_mode = True
                self._state = "answering"

        # 降级模式：直接透传为 answer
        if self._no_tag_mode:
            events.append({"event": "answer", "content": chunk})
            return events

        self._buffer += chunk

        # 主解析循环
        while True:
            if self._state in ("detecting", "answering"):
                tag_name, match_start, match_end = self._find_start_tag(self._buffer)
                if match_start >= 0:
                    # 找到开始标签，将之前的内容作为 answer 发出
                    if match_start > 0:
                        before = self._buffer[:match_start]
                        if self._state == "detecting":
                            self._state = "answering"
                        if before:
                            events.append({"event": "answer", "content": before})
                    self._state = "thinking"
                    self._buffer = self._buffer[match_end:]
                    continue
                else:
                    # 未找到开始标签，保留可能的截断尾部
                    safe_len = self._safe_tail_len()
                    if safe_len > 0 and len(self._buffer) > safe_len:
                        emit = self._buffer[:-safe_len]
                        self._buffer = self._buffer[-safe_len:]
                        if self._state == "detecting":
                            self._state = "answering"
                        if emit:
                            events.append({"event": "answer", "content": emit})
                    elif safe_len == 0 or len(self._buffer) <= safe_len:
                        # 缓冲区太短，全部保留等待下次
                        pass
                    break

            elif self._state == "thinking":
                tag_name, match_start, match_end = self._find_end_tag(self._buffer)
                if match_start >= 0:
                    # 找到结束标签
                    if match_start > 0:
                        before = self._buffer[:match_start]
                        if before:
                            events.append({"event": "thinking", "content": before})
                    self._state = "answering"
                    self._buffer = self._buffer[match_end:]
                    continue
                else:
                    # 未找到结束标签，保留可能的截断尾部
                    safe_len = self._safe_tail_len()
                    if safe_len > 0 and len(self._buffer) > safe_len:
                        emit = self._buffer[:-safe_len]
                        self._buffer = self._buffer[-safe_len:]
                        if emit:
                            events.append({"event": "thinking", "content": emit})
                    break

        return events

    def flush(self) -> list:
        """
        流结束时调用，处理缓冲区残留。
        - 若仍在 thinking 状态 → 将残留全部作为 thinking（标签未闭合兜底）
        - 若在 answering 状态 → 清理残留标签后作为 answer
        """
        events = []
        if self._buffer:
            if self._state == "thinking":
                # 未闭合：全部视为思考内容
                events.append({"event": "thinking", "content": self._buffer})
            elif self._state in ("answering", "detecting"):
                cleaned = self._clean_residual(self._buffer)
                if cleaned.strip():
                    events.append({"event": "answer", "content": cleaned})
            self._buffer = ""
        return events

    # ---------- private helpers ----------

    def _find_start_tag(self, text: str):
        """在 text 中搜索首个匹配的开始标签，返回 (tag_name, start_pos, end_pos) 或 (None, -1, -1)"""
        best_pos = len(text) + 1
        best_result = (None, -1, -1)
        for name, marker in self.START_PATTERNS:
            pos = text.find(marker)
            if pos >= 0 and pos < best_pos:
                best_pos = pos
                best_result = (name, pos, pos + len(marker))
        return best_result

    def _find_end_tag(self, text: str):
        """在 text 中搜索首个匹配的结束标签"""
        best_pos = len(text) + 1
        best_result = (None, -1, -1)
        for name, marker in self.END_PATTERNS:
            pos = text.find(marker)
            if pos >= 0 and pos < best_pos:
                best_pos = pos
                best_result = (name, pos, pos + len(marker))
        return best_result

    def _has_any_start_tag(self, text: str) -> bool:
        """检测文本中是否存在任何开始标签"""
        for _, marker in self.START_PATTERNS:
            if marker in text:
                return True
        return False

    def _safe_tail_len(self) -> int:
        """
        返回缓冲区尾部需保留的字符数，防止标签被截断。
        取所有匹配候选中长度最大的值，防止短候选抢先匹配。
        """
        if not self._buffer:
            return 0
        longest = 0
        for candidate in self.TRUNCATION_CANDIDATES:
            if len(candidate) <= len(self._buffer):
                if self._buffer.endswith(candidate):
                    if len(candidate) > longest:
                        longest = len(candidate)
        return longest

    def _clean_residual(self, text: str) -> str:
        """清理残留标签字符"""
        import re
        for pattern, replacement in self.CLEANUP_RESIDUAL:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        # 清理开头的空行和分隔线
        text = re.sub(r'^\s*---\s*\n?', '', text)
        return text


class RAGSearchService:
    """
    RAG 搜索服务类

    核心业务逻辑封装，包含：
    - LLM 初始化（工具调用和生成器）
    - Reranker 初始化
    - Milvus 连接和集合加载
    - Prompt 模板初始化
    - 会话历史管理
    """

    _instance: Optional["RAGSearchService"] = None

    def __new__(cls):
        """单例模式：确保全局只有一个 RAGService 实例"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """初始化 RAG 服务"""
        if self._initialized:
            return

        logger.info("正在初始化 RAG 搜索服务...")

        self._init_llm()
        self._init_reranker()
        self._connect_milvus()
        self._init_prompts()
        self._init_session_manager()

        self.executor = ThreadPoolExecutor(max_workers=4)

        self._initialized = True
        logger.info("RAG 搜索服务初始化完成 ✅")

    def _init_llm(self):
        """
        初始化 LLM 模型

        创建两个 ChatOpenAI 实例：
        - llm_tool: 低温度（0.1），用于工具调用、查询改写等确定性任务
        - llm_generator: 高温度（0.7），用于答案生成等创造性任务
        """
        self.llm_tool = ChatOpenAI(
            model_name=llm_settings.MODEL_NAME,
            openai_api_base=llm_settings.API_BASE,
            openai_api_key=llm_settings.API_KEY,
            temperature=0.1,
            streaming=True,
        )

        self.llm_generator = ChatOpenAI(
            model_name=llm_settings.MODEL_NAME,
            openai_api_base=llm_settings.API_BASE,
            openai_api_key=llm_settings.API_KEY,
            temperature=0.7,
            streaming=True,
        )

        logger.info(f"LLM 初始化完成: model={llm_settings.MODEL_NAME}")

    def _init_reranker(self):
        """初始化 Rerank 重排序模型"""
        self.reranker = None
        use_rerank = os.getenv("USE_RERANK", "true").lower() == "true"
        if use_rerank:
            try:
                from FlagEmbedding import FlagReranker

                self.reranker = FlagReranker(
                    rerank_settings.MODEL_PATH,
                    use_fp16=True
                )
                logger.info(f"Rerank 模型加载完成: {rerank_settings.MODEL_PATH}")
            except Exception as e:
                logger.warning(f"Rerank 模型加载失败: {e}")

    def _connect_milvus(self):
        """连接 Milvus 并加载 ty_content 集合"""
        logger.info(f"[_connect_milvus] 开始连接 Milvus: {milvus_settings.HOST}:{milvus_settings.PORT}")
        try:
            if not connections.has_connection("default"):
                connections.connect(
                    host=milvus_settings.HOST,
                    port=milvus_settings.PORT,
                    alias="default"
                )
                logger.info(f"[_connect_milvus] Milvus 连接已建立")
            else:
                logger.info(f"[_connect_milvus] Milvus 连接已存在")
            
            self.col_content = self._load_collection(milvus_settings.COLLECTION_NAME)
            logger.info(f"[_connect_milvus] 集合加载结果: {self.col_content}")
            logger.info("Milvus 连接成功")
        except Exception as e:
            logger.error(f"[_connect_milvus] Milvus 连接失败: {e}")
            self.col_content = None
            logger.error(f"Milvus 连接失败: {e}")
            raise e

    def _load_collection(self, name: str) -> Optional[Collection]:
        """加载指定的 Milvus 集合"""
        try:
            if utility.has_collection(name):
                col = Collection(name)
                col.load()
                logger.info(f"集合 {name} 加载成功")
                return col
            else:
                logger.warning(f"集合 {name} 不存在，将跳过该库检索")
                return None
        except Exception as e:
            logger.error(f"加载集合 {name} 异常: {e}")
            return None

    def _init_prompts(self):
        """初始化 LangChain Prompt 模板"""
        self._init_rewrite_prompt()
        self._init_summary_prompt()
        self._init_analysis_prompt()
        self._init_generation_prompt()
        logger.info("Prompt 模板初始化完成")

    def _init_rewrite_prompt(self):
        """初始化查询改写 Prompt"""
        rewrite_system = """
        你是一个查询改写助手。你的任务是根据【对话历史】将用户的【最新问题】改写为一个独立的、包含完整上下文的查询语句，以便进行数据库检索。
        
        规则：
        1. 如果用户的问题依赖上下文（例如"他有多少粉丝"、"那成都呢"），请结合历史补全主语和限定词。
        2. 如果用户的问题已经独立且清晰，请保持原样。
        3. 不要回答问题，只输出改写后的查询语句。
        4. 如果以上三点都不符合，直接保持原样，不要输出任何其他内容！
        """
        self.chain_rewrite = (
            ChatPromptTemplate.from_messages([
                ("system", rewrite_system),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{question}")
            ])
            | self.llm_tool
            | StrOutputParser()
        )

    def _init_summary_prompt(self):
        """初始化历史摘要 Prompt"""
        summary_system = """
        请简要总结以下对话的主要内容，保留关键实体（关键词、时间、地点、已查到的情报结论）。
        摘要应简洁明了，用于辅助后续对话。
        """
        self.chain_summary = (
            ChatPromptTemplate.from_messages([
                ("system", summary_system),
                ("human", "以下是对话历史：\n{history_text}")
            ])
            | self.llm_tool
            | StrOutputParser()
        )

    def _init_analysis_prompt(self):
        
        base_prompt = """
        【当前时间戳为】
        {time}
        【核心原则 & 避坑指南】(非常重要!!!)
        1. IN 操作符语法:
           - 正确: 必须使用 方括号 [] 表示列表。例如: risk_level in ['高危', '中危', '低危']
           - 错误: 严禁使用圆括号 ()。例如: risk_level in ('高危', '中危', '低危') (这是非法语法)。
        2. 关键词匹配:
           - 不要在 expr 中使用 like 进行全文/模糊搜索（如 title like '%关键词%' 是低效且受限的）
           - 所有关于内容、主题、实体的文本检索意图，请直接放入 keywords 字段，利用向量检索的语义能力。
           - expr 仅用于过滤明确的元数据字段（如风险等级、时间、行业、威胁类别等）。
        3. 字符串用单引号，逻辑运算 &&, ||, ==, !=

        1. 结构化情报字段 (重点关注):
            (1) entities_industry (JSON数组): 行业分布。
                * 可选值(固定): ["建筑与房地产", "航空", "政府", "互联网", "能源与公共设施", "生产与制造", "金融", "医疗", "物流", "电商", "教育", "社交", "电信", "国防军工"]
            
            (2) entities_region (JSON对象): 地区分布。
                * 结构: {{"国家": ["中国"...], "省份": ["广东"...], "城市": [["广州"]...]}}
            
            (3) entities_label (JSON对象): 主题标签。
                * 结构 (注意层级):
                    {{
                    "政治军事": {{"政治": [], "军事": []}},
                    "走私贩毒": {{"走私": [], "贩毒": []}},
                    "反恐维稳": {{"暴恐": [], "维稳": [], "赌博": [], "色情": []}},
                    "安全漏洞": {{"漏洞": [], "安全事件": []}},
                    "数据泄露": {{"个人信息": [], "认证与凭证": [], "企业和组织": [], "政府机密": []}},
                    "勒索事件": [],
                    "黑灰产": {{"信息与账号": [], "支付与金融": [], "服务与工具": [], "网络欺诈": [], "流量作弊": []}}
                    }}
        2. JSON 过滤 (使用 json_contains 或 路径引用):
           - 筛选[行业]: 使用 json_contains(entities_industry, '目标行业')
             * 例: "金融行业" -> "json_contains(entities_industry, '金融')"
           
           - 筛选[地区]: 
             * 查国家: "json_contains(entities_region['国家'], '中国')"
             * 查省份: "json_contains(entities_region['省份'], '广东')"
           
           - 筛选[特定实体]: 如果用户查询具体的实体(如某武器、某组织)，可尝试检查特定标签路径。
             * 例: "涉及J-20的军事情報" -> "json_contains(entities_label['政治军事']['军事'], 'J-20')"

        【expr 生成规则】
        1. 基础语法: 字符串用单引号, 逻辑运算 &&, ||, ==, !=.
        2. 风险等级场景:
           - 用户查 "高危或中危" -> risk_level in ['高危', '中危']
        3. 威胁类别场景:
           - 用户查 "数据泄露" -> threat_category == '数据泄露'
        4. 行业场景:-
           - 用户查 "金融行业" -> industry == '金融'
        5. 地区场景:
           - 用户查 "中国" -> region == '中国'
        6. 时间场景:
           - 用户查 "2025年10月01以后" -> publish_time >= 1759248000

        【例子】

        - 用户: "查看成都市的暴恐消息"
          -> keywords: "成都 暴恐", expr: "region == '成都' && risk_level == '高危'"

        - 用户: "查看关于数据泄露的信息，排除低危情报"
          -> keywords: "数据泄露", expr: "risk_level != '低危' && threat_category == '数据泄露'"

        - 用户: "查询金融行业的中危数据"
          -> keywords: "金融", expr: "industry == '金融' && risk_level == '中危'"

        - 用户: "帮我找一下涉及成都或重庆的暴恐消息，只要高危的"
          -> keywords: "成都 重庆 暴恐", expr: "(region == '成都' || region == '重庆') && risk_level == '高危'"

        - 用户: "给我一些2025年10月01以后的金融数据"
          -> keywords: "金融", expr: "publish_time >= 1759248000 && industry == '金融'"
        """

        analysis_system = """
        你是一个精通 Milvus 检索的专家。请根据用户的自然语言问题，生成针对【ty_content】情报集合的查询参数。

        请输出如下 JSON 格式：
        {{
            "keywords": "用于向量搜索的关键词",
            "expr": "过滤表达式字符串 (如无则留空)"
        }}

        【Milvus Schema 参考 - ty_content 集合】
        1. 基础字段:
           - content_id (内容唯一标识)
           - title (标题)
           - text_preview (内容摘要, 2048字符)
           - raw_content (原始内容)
           - platform (来源平台，如 reddit, twitter, telegram等)
           - site_name (网站名称)
           - author_name (作者/发布者)
           - threat_category (威胁类别: 数据泄露, 网络攻击, 钓鱼, 暴恐, 勒索, 黑灰产等)
           - risk_level (风险等级: 高危, 中危, 低危)
           - industry (行业: 金融, 互联网, 政府, 医疗, 教育, 电信, 能源, 航空, 建筑, 制造, 物流, 电商, 社交, 国防军工等)
           - risk_score (风险分数, 0-100)
           - region (地区)
           - publish_time (时间戳, int64)
           - url (原文链接)
           - topic (主题)
           - entity_tags (实体标签简表)
        """ + base_prompt

        self.chain_analysis = (
            ChatPromptTemplate.from_messages([
                ("system", analysis_system),
                ("human", "{question}")
            ])
            | self.llm_tool
            | StrOutputParser()
        )

    def _init_generation_prompt(self):
        """初始化答案生成 Prompt"""
        gen_system = """
        你是一名专业的情报分析师。请根据提供的【参考情报】和【对话上下文】，回答用户的问题。

        【回答结构要求 - 必须严格遵循】
        你的回答必须按照以下结构分点输出，使用清晰的 Markdown 格式：

        ## 📋 概述
        - 简要概括事件的核心内容（时间、地点、人物、起因、经过、结果）。
        - 提炼关键信息摘要。

        ## 🚨 事件分析
        - **行业分布**：涉及的行业领域。
        - **地区分布**：涉及的国家、省份、城市。
        - **话题焦点**：主要讨论的话题（如数据泄露、军事行动、网络攻击等）。
        - **来源分析**：情报的主要来源渠道（Deep Web / Telegram / Surface Web）。

        ## 👥 人物与组织
        - **关键人物**：提及的重要个人（身份、背景、关系）。
        - **组织机构**：涉及的组织、团体、公司。
        - **行为轨迹**：相关实体的活动记录或关联行为。

        ## ⚖️ 研判结论与建议
        - **风险评估**：整体风险等级 [高危/中危/低危] 及理由。
        - **研判结论**：基于情报的最终判断。
        - **处置建议**：针对该事件的建议应对措施。

        【内容要求】
        1. **结构化**：严格按上述标题分块，不要合并或省略。
        2. **引用**：关键事实请在句尾自动标注来源序号，如 [1]。
        3. **客观性**：基于提供的情报数据回答，不要编造。
        4. **高亮**：对重要实体（人名、地名、组织名）使用 **加粗** 标注。

        【参考情报】
         {context}

         请严格按照上述结构输出回答。

         【重要】请使用中文进行思考和推理。思考过程应聚焦于分析逻辑，不得预先撰写完整的最终回答。思考过程应精炼、有条理。"""
        self.chain_gen = (
            ChatPromptTemplate.from_messages([
                ("system", gen_system),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{question}")
            ])
            | self.llm_generator
            | StrOutputParser()
        )

    def _init_session_manager(self):
        """初始化会话管理器"""
        self.history_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "chat_history_search"
        )
        os.makedirs(self.history_dir, exist_ok=True)
        self.sessions: Dict[str, Dict] = {}

    # ================== 公开 API 方法 ==================

    def search(
        self,
        question: str,
        session_id: str,
        use_rerank: bool = True
    ) -> Dict[str, Any]:
        """
        RAG 搜索主入口

        执行完整的 RAG 搜索流程：
        1. 查询改写（结合历史上下文）
        2. 检索 ty_content 集合
        3. Rerank 重排序
        4. 生成最终回答
        5. 更新对话历史

        Args:
            question: 用户问题
            session_id: 会话 ID
            use_rerank: 是否使用重排序

        Returns:
            Dict 包含 answer, sources, session_id, model
        """
        self._ensure_session_loaded(session_id)

        rewritten_question = self._rewrite_question(question, session_id)
        logger.info(f"改写后的问题: {rewritten_question}")

        all_results = self._search_content(rewritten_question)
        logger.info(f"原始检索结果: {len(all_results)}")

        if use_rerank and self.reranker:
            all_results = self._rerank_results(question, all_results)
            logger.info(f"Rerank 后结果: {len(all_results)}")

        all_results = all_results[:20]

        answer = self._generate_answer(question, all_results, session_id)
        self._manage_history(session_id, question, answer)

        result = {
            "answer": answer,
            "sources": all_results,
            "session_id": session_id,
            "model": llm_settings.MODEL_NAME
        }
        
        return result

    def _rewrite_question(self, question: str, session_id: str) -> str:
        """
        查询改写

        根据对话历史将用户问题改写为包含完整上下文的形式

        Args:
            question: 原始问题
            session_id: 会话 ID

        Returns:
            改写后的查询语句
        """
        logger.info(f"[_rewrite_question] 开始改写, question: {question}, session_id: {session_id}")
        session = self.sessions.get(session_id, {})
        history = session.get("history", [])
        logger.info(f"[_rewrite_question] 历史记录数量: {len(history)}")
        if history:
            recent_history = history[-4:]
            for i, msg in enumerate(recent_history):
                logger.info(f"[_rewrite_question]   history[-{len(recent_history)-i}]: {msg.type}: {msg.content[:100]}")

        try:
            rewritten = self.chain_rewrite.invoke({
                "question": question,
                "history": history
            })
            result = rewritten.strip() if rewritten else question
            logger.info(f"[_rewrite_question] 改写结果: {result}")
            return result
        except Exception as e:
            logger.error(f"[_rewrite_question] 查询改写失败: {e}")
            return question

    def _search_content(self, question: str) -> List[Dict[str, Any]]:
        """
        ty_content 集合检索

        Args:
            question: 改写后的查询语句

        Returns:
            检索结果列表
        """
        logger.info(f"[_search_content] 开始检索, question: {question}")
        if not self.col_content:
            logger.warning("[_search_content] col_content 为 None，返回空列表")
            return []

        try:
            logger.info(f"[_search_content] 调用 _analyze_query...")
            query_params = self._analyze_query(question)
            keywords = query_params.get("keywords", question)
            expr = query_params.get("expr", "")
            logger.info(f"[_search_content] 查询参数: keywords={keywords}, expr={expr}")

            search_params = {
                "metric_type": "IP",
                "params": {"nprobe": 10}
            }

            logger.info(f"[_search_content] 执行向量搜索...")
            results = self.col_content.search(
                data=[self._get_embedding(keywords)],
                anns_field="vector",
                param=search_params,
                limit=100,
                expr=expr if expr else None,
                output_fields=[
                    "content_id", "title", "text_preview", "raw_content",
                    "platform", "site_name", "author_name", "threat_category",
                    "risk_level", "industry", "risk_score", "region",
                    "publish_time", "url",
                    "topic", "entity_tags"
                ]
            )
            logger.info(f"[_search_content] 搜索完成，初步结果数量: {len(results)}")

            parsed_results = self._parse_content_results(results)
            logger.info(f"[_search_content] 解析后结果数量: {len(parsed_results)}")
            return parsed_results
        except Exception as e:
            logger.error(f"[_search_content] ty_content 检索失败: {e}")
            return []

    def _analyze_query(self, question: str) -> Dict[str, str]:
        """
        使用 LLM 分析用户问题，生成检索参数

        Args:
            question: 用户问题

        Returns:
            {"keywords": "...", "expr": "..."}
        """
        logger.info(f"[_analyze_query] 开始分析问题: {question}")
        try:
            result = self.chain_analysis.invoke({"question": question, "time": int(time.time())})
            logger.info(f"[_analyze_query] LLM 原始输出: {result}")
            
            if not result or not result.strip():
                logger.warning("[_analyze_query] LLM 返回空内容，使用原始问题作为关键词")
                return {"keywords": question, "expr": ""}
            
            json_str = result.strip()
            json_start = json_str.find('{')
            if json_start == -1:
                logger.error(f"[_analyze_query] LLM 输出中未找到 JSON: {result}")
                return {"keywords": question, "expr": ""}
            
            json_str = json_str[json_start:]
            last_brace = json_str.rfind('}')
            if last_brace != -1:
                json_str = json_str[:last_brace + 1]
            
            parsed = json.loads(json_str)
            logger.info(f"[_analyze_query] 解析成功: keywords={parsed.get('keywords')}, expr={parsed.get('expr')}")
            return parsed
        except json.JSONDecodeError as e:
            logger.error(f"[_analyze_query] JSON 解析失败: {e}，LLM 输出: {result}")
            return {"keywords": question, "expr": ""}
        except Exception as e:
            logger.error(f"[_analyze_query] 查询分析失败: {e}")
            return {"keywords": question, "expr": ""}

    def _get_embedding(self, text: str) -> List[float]:
        """
        获取文本的向量嵌入

        Args:
            text: 输入文本

        Returns:
            向量列表
        """
        try:
            import httpx
            url = f"{milvus_settings.EMBEDDING_API_URL.rstrip('/')}"
            payload = {"input": text, "model": "embedding-model"}
            headers = {"Content-Type": "application/json"}

            with httpx.Client(timeout=30.0) as client:
                response = client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                result = response.json()
                raw_vec = result["data"][0]["embedding"]
                norm = math.sqrt(sum(x * x for x in raw_vec))
                return [x / norm for x in raw_vec] if norm > 0 else raw_vec
        except Exception as e:
            logger.error(f"获取 embedding 失败: {e}")
            return [0.0] * milvus_settings.DIMENSION

    def _parse_content_results(self, results) -> List[Dict[str, Any]]:
        """
        解析 ty_content 搜索结果

        Args:
            results: Milvus 搜索结果

        Returns:
            标准化后的结果列表（包含相似度分数）
        """
        parsed = []
        for hit in results:
            for entity in hit:
                ip_distance = getattr(entity, 'distance', None)
                if ip_distance is not None:
                    similarity_score = max(0.0, min(1.0, (ip_distance + 1.0) / 2.0))
                else:
                    similarity_score = 0.0
                item = {
                    "content_id": entity.get("content_id", ""),
                    "title": entity.get("title", ""),
                    "text_preview": entity.get("text_preview", ""),
                    "raw_content": entity.get("raw_content", ""),
                    "platform": entity.get("platform", ""),
                    "site_name": entity.get("site_name", ""),
                    "author_name": entity.get("author_name", ""),
                    "threat_category": entity.get("threat_category", ""),
                    "risk_level": entity.get("risk_level", ""),
                    "industry": entity.get("industry", ""),
                    "risk_score": entity.get("risk_score", 0.0),
                    "region": entity.get("region", ""),
                    "publish_time": entity.get("publish_time", 0),
                    "url": entity.get("url", ""),
                    "topic": entity.get("topic", ""),
                    "entity_tags": json.loads(entity.get("entity_tags", "[]")),
                    "similarity_score": similarity_score,
                }
                parsed.append(item)
        return parsed

    def _rerank_results(
        self,
        question: str,
        results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Rerank 重排序

        使用重排序模型对检索结果进行二次排序

        Args:
            question: 用户问题
            results: 原始检索结果

        Returns:
            重排序后的结果列表
        """
        if not results or not self.reranker:
            return results

        try:
            pairs = [
                [question, item.get("title", "") + " " + item.get("text_preview", "")]
                for item in results
            ]
            scores = self.reranker.compute_score(pairs)

            for i, item in enumerate(results):
                item["rerank_score"] = scores[i] if i < len(scores) else 0.0

            results.sort(key=lambda x: x.get("rerank_score", 0), reverse=True)
            return results
        except Exception as e:
            logger.error(f"Rerank 失败: {e}")
            return results

    def _generate_answer(
        self,
        question: str,
        context: List[Dict[str, Any]],
        session_id: str
    ) -> str:
        """
        生成最终回答

        Args:
            question: 用户问题
            context: 参考上下文
            session_id: 会话 ID

        Returns:
            生成的答案
        """
        session = self.sessions.get(session_id, {})
        history = session.get("history", [])

        context_text = self._format_context(context)

        try:
            answer = self.chain_gen.invoke({
                "question": question,
                "context": context_text,
                "history": history
            })
            return answer
        except Exception as e:
            logger.error(f"答案生成失败: {e}")
            return "抱歉，生成回答时出现错误。"

    async def generate_answer_stream(
        self,
        question: str,
        context: List[Dict[str, Any]],
        session_id: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        流式生成最终回答

        Args:
            question: 用户问题
            context: 参考上下文
            session_id: 会话 ID

        Yields:
            Dict 包含事件类型和内容
            - event: "thinking" | "answer" | "done" | "error"
            - content: 内容字符串
        """
        session = self.sessions.get(session_id, {})
        history = session.get("history", [])
        context_text = self._format_context(context)

        gen_system = """
        你是一名专业的情报分析师。请根据提供的【参考情报】和【对话上下文】，回答用户的问题。

        【回答结构要求 - 必须严格遵循】
        你的回答必须按照以下结构分点输出，使用清晰的 Markdown 格式：

        ## 📋 概述
        - 简要概括事件的核心内容（时间、地点、人物、起因、经过、结果）。
        - 提炼关键信息摘要。

        ## 🚨 事件分析
        - **行业分布**：涉及的行业领域。
        - **地区分布**：涉及的国家、省份、城市。
        - **话题焦点**：主要讨论的话题（如数据泄露、军事行动、网络攻击等）。
        - **来源分析**：情报的主要来源渠道（Deep Web / Telegram / Surface Web）。

        ## 👥 人物与组织
        - **关键人物**：提及的重要个人（身份、背景、关系）。
        - **组织机构**：涉及的组织、团体、公司。
        - **行为轨迹**：相关实体的活动记录或关联行为。

        ## ⚖️ 研判结论与建议
        - **风险评估**：整体风险等级 [高危/中危/低危] 及理由。
        - **研判结论**：基于情报的最终判断。
        - **处置建议**：针对该事件的建议应对措施。

        【内容要求】
        1. **结构化**：严格按上述标题分块，不要合并或省略。
        2. **引用**：关键事实请在句尾自动标注来源序号，如 [1]。
        3. **客观性**：基于提供的情报数据回答，不要编造。
        4. **高亮**：对重要实体（人名、地名、组织名）使用 **加粗** 标注。

        【参考情报】
        """ + context_text + """

        请严格按照上述结构输出回答。

        【重要】请使用中文进行思考和推理。思考过程应聚焦于分析逻辑，不得预先撰写完整的最终回答。思考过程应精炼、有条理。最终回答也必须使用中文输出。"""


        messages = [
            {"role": "system", "content": gen_system},
        ]
        for msg in history:
            if isinstance(msg, HumanMessage):
                messages.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                messages.append({"role": "assistant", "content": msg.content})
        messages.append({"role": "user", "content": question})

        payload = {
            "model": llm_settings.MODEL_NAME,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2000,
            "stream": True,
            "extra_body": {"enable_thinking": True},
        }

        url = f"{llm_settings.API_BASE.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {llm_settings.API_KEY}",
            "Content-Type": "application/json",
        }

        try:
            import httpx
            logger.info(f"[generate_answer_stream] 🚀 开始流式生成，模型: {llm_settings.MODEL_NAME}，问题: {question[:100]}...")

            # 内容标签解析器：处理嵌入在 content 字段中的 <think> 标签
            content_parser = StreamTagParser()

            think_phase_started = False
            answer_phase_started = False
            total_thinking_chars = 0
            total_answer_chars = 0

            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream("POST", url, headers=headers, json=payload) as response:
                    logger.info(f"[generate_answer_stream] API 响应状态: {response.status_code}")
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:]
                            if data_str == "[DONE]":
                                logger.info(f"[generate_answer_stream] 收到 [DONE] 信号")
                                break
                            try:
                                chunk = json.loads(data_str)
                                delta = ((chunk.get("choices") or [{}])[0] or {}).get("delta") or {}
                                logger.debug(f"[generate_answer_stream] delta: {delta}")

                                reasoning_delta = delta.get("reasoning") or ""
                                content_delta = delta.get("content") or ""

                                if not reasoning_delta and not content_delta:
                                    reasoning_delta = delta.get("reasoning_content") or ""
                                if not reasoning_delta and not content_delta:
                                    content_delta = delta.get("text") or delta.get("message") or ""

                                # 优先使用 API 提供的独立 reasoning 字段
                                if reasoning_delta:
                                    if not think_phase_started:
                                        logger.info(f"[generate_answer_stream] 🧠 ===== 开始输出思考过程 (reasoning 字段) =====")
                                        think_phase_started = True
                                    total_thinking_chars += len(reasoning_delta)
                                    logger.debug(f"[generate_answer_stream] 发送 thinking 事件(reasoning字段)，长度: {len(reasoning_delta)}")
                                    yield {"event": "thinking", "content": reasoning_delta}

                                # 对 content 字段运行标签解析器（处理 <think> 嵌入）
                                if content_delta:
                                    parsed_events = content_parser.feed(content_delta)
                                    for evt in parsed_events:
                                        if evt["event"] == "thinking":
                                            if not think_phase_started:
                                                logger.info(f"[generate_answer_stream] 🧠 ===== 开始输出思考过程 (content 标签解析) =====")
                                                think_phase_started = True
                                            total_thinking_chars += len(evt['content'])
                                            logger.debug(f"[generate_answer_stream] 发送 thinking 事件(标签解析)，长度: {len(evt['content'])}")
                                        else:
                                            if not answer_phase_started:
                                                if think_phase_started:
                                                    logger.info(f"[generate_answer_stream] ✅ 思考过程输出完成 (共 {total_thinking_chars} 字符)")
                                                logger.info(f"[generate_answer_stream] 📝 ===== 开始输出最终答案 =====")
                                                answer_phase_started = True
                                            total_answer_chars += len(evt['content'])
                                            logger.debug(f"[generate_answer_stream] 发送 answer 事件(标签解析)，长度: {len(evt['content'])}")
                                        yield evt
                            except json.JSONDecodeError as e:
                                logger.warning(f"[generate_answer_stream] JSON 解析失败: {e}, data_str: {data_str[:200]}")
                                continue

                    # 流结束：刷新解析器缓冲区中的残留内容
                    flush_events = content_parser.flush()
                    for evt in flush_events:
                        logger.debug(f"[generate_answer_stream] flush 事件: {evt['event']}, 长度: {len(evt['content'])}")
                        yield evt

                    # 流式输出完成总结
                    if think_phase_started and not answer_phase_started:
                        logger.info(f"[generate_answer_stream] ⚠️ 思考过程输出完成 (共 {total_thinking_chars} 字符)，但未检测到独立答案内容")
                    logger.info(f"[generate_answer_stream] ✨ 流式输出完成 | 思考: {total_thinking_chars} 字符 | 答案: {total_answer_chars} 字符")
                    yield {"event": "done", "content": ""}
        except Exception as e:
            logger.error(f"[generate_answer_stream] 流式生成失败: {e}")
            yield {"event": "error", "content": str(e)}

    def _format_context(self, context: List[Dict[str, Any]]) -> str:
        """
        格式化上下文为文本

        Args:
            context: 检索结果列表

        Returns:
            格式化的文本
        """
        lines = []
        for i, item in enumerate(context, 1):
            line = f"[{i}] {item.get('title', '')}\n"
            line += f"    {item.get('text_preview', '')}\n"
            line += f"    来源: {item.get('platform', '')} | "
            line += f"风险等级: {item.get('risk_level', '')} | "
            line += f"行业: {item.get('industry', '')} | "
            line += f"地区: {item.get('region', '')} | "
            line += f"主题: {item.get('topic', '')}"
            tags = item.get('entity_tags', [])
            if tags:
                line += f" | 标签: {', '.join(tags)}"
            lines.append(line)
        return "\n".join(lines)

    def _manage_history(self, session_id: str, question: str, answer: str):
        """
        管理对话历史

        Args:
            session_id: 会话 ID
            question: 用户问题
            answer: AI 回答
        """
        session = self.sessions[session_id]
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        session["all_history"].append({
            "type": "human",
            "content": question,
            "time": timestamp
        })
        session["all_history"].append({
            "type": "ai",
            "content": answer,
            "time": timestamp
        })

        session["history"].append(HumanMessage(content=question))
        session["history"].append(AIMessage(content=answer))

        if len(session["history"]) > 20:
            self._summarize_history(session_id)

        self._save_history_to_disk(session_id)

    def _summarize_history(self, session_id: str):
        """
        摘要过长的历史记录

        Args:
            session_id: 会话 ID
        """
        session = self.sessions[session_id]
        history = session["history"]

        mid_idx = len(history) // 2
        if mid_idx % 2 != 0:
            mid_idx += 1

        to_summarize = history[:mid_idx]
        recent_history = history[mid_idx:]

        history_text = "\n".join([
            f"{m.type}: {m.content}" for m in to_summarize
        ])
        if session["summary"]:
            history_text = f"前情提要: {session['summary']}\n" + history_text

        try:
            new_summary = self.chain_summary.invoke({"history_text": history_text})
            session["summary"] = new_summary
            session["history"] = recent_history
            logger.info("历史摘要更新完成")
        except Exception as e:
            logger.error(f"摘要生成失败: {e}")

    def get_history(self, session_id: str) -> Dict[str, Any]:
        """
        获取会话历史

        Args:
            session_id: 会话 ID

        Returns:
            历史记录字典
        """
        self._ensure_session_loaded(session_id)
        session = self.sessions[session_id]
        return {
            "session_id": session_id,
            "name": session["name"],
            "summary": session["summary"],
            "history": session.get("all_history", [])
        }

    def clear_history(self, session_id: str):
        """
        清除会话历史

        Args:
            session_id: 会话 ID
        """
        if session_id in self.sessions:
            self.sessions[session_id] = {
                "name": time.strftime("%Y年%m月%d日%H:%M:%S 对话记录"),
                "history": [],
                "summary": "",
                "all_history": []
            }
            self._save_history_to_disk(session_id)

    def _ensure_session_loaded(self, session_id: str):
        """确保会话已加载"""
        logger.info(f"[_ensure_session_loaded] 检查会话: {session_id}")
        if session_id in self.sessions:
            logger.info(f"[_ensure_session_loaded] 会话已存在: {session_id}")
            return

        logger.info(f"[_ensure_session_loaded] 会话不存在，创建新会话: {session_id}")
        self.sessions[session_id] = {
            "name": "新会话",
            "history": [],
            "summary": "",
            "all_history": []
        }
        logger.info(f"[_ensure_session_loaded] 新会话已创建: {session_id}")

        file_path = self._get_history_file_path(session_id)
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                deserialized_history = []
                for item in data.get("history", []):
                    if item["type"] == "human":
                        deserialized_history.append(HumanMessage(content=item["content"]))
                    elif item["type"] == "ai":
                        deserialized_history.append(AIMessage(content=item["content"]))

                self.sessions[session_id] = {
                    "name": data.get("name", "未命名会话"),
                    "history": deserialized_history,
                    "summary": data.get("summary", ""),
                    "all_history": data.get("all_history", [])
                }
                logger.info(f"会话 [{session_id}] 已从磁盘加载")
                return
            except Exception as e:
                logger.error(f"加载历史记录异常: {e}")

        self.sessions[session_id] = {
            "name": time.strftime("%Y年%m月%d日%H:%M:%S 对话记录"),
            "history": [],
            "summary": "",
            "all_history": []
        }
        logger.info(f"新会话初始化: {session_id}")

    def _get_history_file_path(self, session_id: str) -> str:
        """获取历史记录文件路径"""
        safe_sid = "".join([
            c if c.isalnum() or c in "-_" else "_" for c in session_id
        ])
        return os.path.join(self.history_dir, f"{safe_sid}.json")

    def _save_history_to_disk(self, session_id: str):
        """保存历史记录到磁盘"""
        if session_id not in self.sessions:
            return

        session = self.sessions[session_id]
        file_path = self._get_history_file_path(session_id)

        serialized_history = []
        for msg in session["history"]:
            if isinstance(msg, HumanMessage):
                serialized_history.append({"type": "human", "content": msg.content})
            elif isinstance(msg, AIMessage):
                serialized_history.append({"type": "ai", "content": msg.content})

        data_to_save = {
            "name": session.get("name", "未命名会话"),
            "summary": session["summary"],
            "history": serialized_history,
            "all_history": session["all_history"],
            "updated_at": time.time()
        }

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存历史记录失败: {e}")


rag_search_service = RAGSearchService()

if __name__ == "__main__":
    print("=" * 60)
    print("RAG Search Service 公开 API 测试")
    print("=" * 60)
    
    test_session_id = "test_api_session01"
    

    
    print("\n[测试 1] 测试 search 方法 (简单查询)")
    print("-" * 40)
    test_question = "查看有关毒品的消息"
    try:
        result = rag_search_service.search(
            question=test_question,
            session_id=test_session_id,
            use_rerank=False
        )
        print(f"✅ search 执行成功")
        print(f"   返回字段: {list(result.keys())}")
        print(f"   sources 数量: {len(result.get('sources', []))}")
        print(f"   model: {result.get('model')}")
        print(f"   answer 长度: {len(result.get('answer', ''))} 字符")
        print(f"   answer 前100字符: {result.get('answer', '')[:100]}...")
        
        # 显示检索结果的详细信息（JSON格式）
        print(f"\n   📊 Milvus 检索结果详情（前10条，JSON格式）:")
        sources = result.get('sources', [])
        for i, source in enumerate(sources[:10], 1):
            display_source = source.copy()
            score = display_source.get('similarity_score')
            if score is not None:
                display_source['similarity_score_display'] = f"余弦相似度: {score:.4f} (0~1, 越大越相似)"
            else:
                display_source['similarity_score_display'] = None
            
            print(f"\n   [{'='*20} 结果 {i} {'='*20}]")
            print(json.dumps(display_source, ensure_ascii=False, indent=6))
    except Exception as e:
        print(f"❌ search 执行失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n[测试 2] 测试带历史的 search 方法 (上下文查询)")
    print("-" * 40)
    follow_up_question = "那有关数据泄露呢"
    try:
        result = rag_search_service.search(
            question=follow_up_question,
            session_id=test_session_id,
            use_rerank=False
        )
        print(f"✅ follow-up search 执行成功")
        print(f"   原始问题: {test_question}")
        print(f"   追问: {follow_up_question}")
        print(f"   返回字段: {list(result.keys())}")
        print(f"   sources 数量: {len(result.get('sources', []))}")
        print(f"   model: {result.get('model')}")
        print(f"   answer 长度: {len(result.get('answer', ''))} 字符")
        print(f"   answer 前100字符: {result.get('answer', '')[:100]}...")
        
        # 显示检索结果的详细信息（JSON格式）
        print(f"\n   📊 Milvus 检索结果详情（前10条，JSON格式）:")
        sources = result.get('sources', [])
        for i, source in enumerate(sources[:10], 1):
            display_source = source.copy()
            score = display_source.get('similarity_score')
            if score is not None:
                display_source['similarity_score_display'] = f"余弦相似度: {score:.4f} (0~1, 越大越相似)"
            else:
                display_source['similarity_score_display'] = None
            
            print(f"\n   [{'='*20} 结果 {i} {'='*20}]")
            print(json.dumps(display_source, ensure_ascii=False, indent=6))
    except Exception as e:
        print(f"❌ follow-up search 执行失败: {e}")
        import traceback
        traceback.print_exc()
    
    
    print("\n[测试 3] 验证历史记录是否正确保存")
    print("-" * 40)
    try:
        history = rag_search_service.get_history(test_session_id)
        print(f"✅ 历史记录验证成功")
        print(f"   对话轮次: {len(history.get('history', []))}")
        for i, msg in enumerate(history.get('history', [])):
            print(f"   [{i+1}] {msg.get('type')}: {msg.get('content', '')[:50]}...")
    except Exception as e:
        print(f"❌ 历史记录验证失败: {e}")

    print("\n[测试 4] 测试 get_history 方法")
    print("-" * 40)
    try:
        history = rag_search_service.get_history(test_session_id)
        print(f"✅ get_history 执行成功")
        print(f"   session_id: {history.get('session_id')}")
        print(f"   name: {history.get('name')}")
        print(f"   history count: {len(history.get('history', []))}")
    except Exception as e:
        print(f"❌ get_history 执行失败: {e}")

    print("\n[测试 5] 测试 clear_history 方法")
    print("-" * 40)
    try:
        rag_search_service.clear_history(test_session_id)
        print("✅ clear_history 执行成功")
    except Exception as e:
        print(f"❌ clear_history 执行失败: {e}")
    
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
