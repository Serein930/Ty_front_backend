"""
Deep Analyzer 模块
================

该模块提供深度情报分析功能。

主要功能：
- 多维度情报分析
- 实体提取和关系图谱构建
- 威胁评估和风险评分
- 情报关联分析

使用场景：
- RAG 搜索结果的深度加工
- 情报数据的二次分析
- 威胁实体追踪

依赖：
- langchain>=0.1.0
"""

from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class IntelligenceAnalyzer:
    """
    情报深度分析器

    提供多维度的情报分析功能：
    - 实体提取
    - 关系分析
    - 威胁评估
    - 风险评分
    """

    def __init__(self):
        """初始化分析器"""
        logger.info("初始化深度分析器...")

        try:
            from langchain_openai import ChatOpenAI
            from app.config.config import llm_settings

            self.llm = ChatOpenAI(
                model_name=llm_settings.MODEL_NAME,
                openai_api_base=llm_settings.API_BASE,
                openai_api_key=llm_settings.API_KEY,
                temperature=0.3
            )
            logger.info("深度分析器 LLM 初始化完成")
        except Exception as e:
            logger.error(f"深度分析器 LLM 初始化失败: {e}")
            self.llm = None

    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        从文本中提取实体

        Args:
            text: 输入文本

        Returns:
            实体列表，每项包含 type, name, confidence
        """
        if not self.llm:
            return []

        prompt = f"""
        请从以下文本中提取所有实体（人物、组织、地点、事件等）。
        只输出 JSON 数组格式，不要其他内容。

        文本：
        {text[:2000]}

        输出格式：
        [
            {{"type": "人物", "name": "张三", "confidence": 0.95}},
            {{"type": "组织", "name": "XX公司", "confidence": 0.88}}
        ]
        """

        try:
            from langchain_core.output_parsers import StrOutputParser
            from langchain_core.prompts import ChatPromptTemplate

            chain = (
                ChatPromptTemplate.from_messages([("human", prompt)])
                | self.llm
                | StrOutputParser()
            )

            result = chain.invoke({})
            import json
            return json.loads(result)
        except Exception as e:
            logger.error(f"实体提取失败: {e}")
            return []

    def analyze_relations(self, entities: List[Dict]) -> List[Dict]:
        """
        分析实体之间的关系

        Args:
            entities: 实体列表

        Returns:
            关系列表
        """
        if not self.llm or not entities:
            return []

        entities_str = "\n".join([
            f"- {e.get('type')}: {e.get('name')}"
            for e in entities
        ])

        prompt = f"""
        请分析以下实体之间的关系。

        实体列表：
        {entities_str}

        输出 JSON 数组格式：
        [
            {{"source": "实体1", "target": "实体2", "relation": "关系描述", "confidence": 0.9}}
        ]
        """

        try:
            from langchain_core.output_parsers import StrOutputParser
            from langchain_core.prompts import ChatPromptTemplate

            chain = (
                ChatPromptTemplate.from_messages([("human", prompt)])
                | self.llm
                | StrOutputParser()
            )

            result = chain.invoke({})
            import json
            return json.loads(result)
        except Exception as e:
            logger.error(f"关系分析失败: {e}")
            return []

    def threat_assessment(self, data: Dict) -> Dict:
        """
        威胁评估

        Args:
            data: 包含情报数据的字典

        Returns:
            威胁评估结果
        """
        if not self.llm:
            return {"level": "未知", "score": 0, "reasoning": "分析器不可用"}

        prompt = f"""
        请对以下情报进行威胁评估。

        情报内容：
        标题: {data.get('title', '')}
        内容: {data.get('text_preview', '')[:1000]}
        来源: {data.get('platform', '')}
        风险等级: {data.get('threaten_level', '')}

        请输出 JSON 格式：
        {{
            "level": "高危/中危/低危",
            "score": 0-100的分数,
            "reasoning": "评估理由",
            "key_concerns": ["主要关注点1", "主要关注点2"]
        }}
        """

        try:
            from langchain_core.output_parsers import StrOutputParser
            from langchain_core.prompts import ChatPromptTemplate

            chain = (
                ChatPromptTemplate.from_messages([("human", prompt)])
                | self.llm
                | StrOutputParser()
            )

            result = chain.invoke({})
            import json
            return json.loads(result)
        except Exception as e:
            logger.error(f"威胁评估失败: {e}")
            return {"level": "未知", "score": 0, "reasoning": str(e)}

    def generate_report(self, data_list: List[Dict]) -> str:
        """
        生成综合分析报告

        Args:
            data_list: 情报数据列表

        Returns:
            Markdown 格式的分析报告
        """
        if not self.llm:
            return "分析器不可用"

        context = "\n\n".join([
            f"### {item.get('title', '无标题')}\n"
            f"- 来源: {item.get('platform', '')}\n"
            f"- 摘要: {item.get('text_preview', '')[:500]}\n"
            f"- 风险: {item.get('threaten_level', '')}"
            for item in data_list[:10]
        ])

        prompt = f"""
        请根据以下情报数据，生成一份综合分析报告。

        {context}

        报告要求：
        1. 概述整体态势
        2. 分析主要威胁
        3. 识别关键实体
        4. 给出处置建议
        """

        try:
            from langchain_core.output_parsers import StrOutputParser
            from langchain_core.prompts import ChatPromptTemplate

            chain = (
                ChatPromptTemplate.from_messages([("human", prompt)])
                | self.llm
                | StrOutputParser()
            )

            return chain.invoke({})
        except Exception as e:
            logger.error(f"报告生成失败: {e}")
            return f"报告生成失败: {e}"
