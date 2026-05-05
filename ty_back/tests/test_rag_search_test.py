"""
RAG Search 综合测试脚本
========================

测试流程：
1. 查询改写 — 显示 LLM 改写后的问题
2. 查询分析 — 显示 LLM 生成的检索参数（keywords + expr）
3. 向量归一化验证 — 验证 Embedding 的 L2 范数 ≈ 1.0
4. 向量检索 — 显示 Milvus 返回的 Top-10 结果及相似度分数
5. 流式生成 — 实时展示模型的思考过程和最终输出（主流 AI 风格）

核心验证点：
- Embedding 是否正确做了 L2 归一化（norm ≈ 1.0）
- 归一化向量 + IP 内积搜索 = 余弦相似度
- similarity_score = clamp((IP + 1.0) / 2.0, 0, 1) 映射正确

测试模型：Qwen3.6-35B-A3B
"""

import os
import sys
import json
import math
import time
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx
from app.config.config import llm_settings
from app.services.rag_search_service import rag_search_service
from app.milvus.service import get_embedding as milvus_get_embedding


# ==================== 日志配置 ====================

LOG_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "app", "logs"
)
os.makedirs(LOG_DIR, exist_ok=True)

log_file = os.path.join(LOG_DIR, f"rag_test_{time.strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ],
    force=True
)

logger = logging.getLogger("rag_test")

# ==================== 测试配置 ====================

TEST_SESSION_ID = "test_drug_search_session"
TEST_QUESTION = "给我有关毒品的数据信息"


# ==================== 辅助函数 ====================

def print_separator(title: str):
    line = "=" * 70
    logger.info("")
    logger.info(line)
    logger.info(f"  {title}")
    logger.info(line)


# ==================== 步骤函数 ====================

def step1_rewrite_question() -> str:
    """步骤1: 查询改写 — 展示改写后的问题"""
    print_separator("步骤 1/5: 查询改写 (Query Rewriting)")

    logger.info(f"📥 原始问题: {TEST_QUESTION}")

    rag_search_service._ensure_session_loaded(TEST_SESSION_ID)
    rewritten = rag_search_service._rewrite_question(TEST_QUESTION, TEST_SESSION_ID)

    logger.info(f"🔄 改写后的问题: {rewritten}")
    return rewritten


def step2_analyze_query(rewritten: str):
    """步骤2: 查询分析 — 展示 LLM 生成的检索参数"""
    print_separator("步骤 2/5: 查询分析 (Query Analysis)")

    logger.info(f"📥 输入: {rewritten}")
    query_params = rag_search_service._analyze_query(rewritten)

    logger.info(f"📊 查询参数:")
    logger.info(json.dumps(query_params, ensure_ascii=False, indent=2))
    return query_params


def step3_verify_normalization():
    """步骤3: 向量归一化验证 — 验证 Embedding L2 范数 ≈ 1.0"""
    print_separator("步骤 3/5: 向量归一化验证 (Normalization Verification)")

    logger.info("📥 验证文本: " + TEST_QUESTION)
    logger.info("")

    # === 通过 rag_search_service 获取归一化向量 ===
    vector_svc = rag_search_service._get_embedding(TEST_QUESTION)
    norm_svc = math.sqrt(sum(x * x for x in vector_svc))

    logger.info(f"📐 [rag_search_service._get_embedding]")
    logger.info(f"   向量维度: {len(vector_svc)}")
    logger.info(f"   向量前 5 个元素: {vector_svc[:5]}")
    logger.info(f"   L2 范数: {norm_svc:.10f}  {'✅ ≈ 1.0 (归一化正确)' if abs(norm_svc - 1.0) < 1e-6 else '❌ != 1.0'}")

    # === 通过 milvus/service.py 获取归一化向量（一致性验证） ===
    vector_milvus = milvus_get_embedding(TEST_QUESTION)
    norm_milvus = math.sqrt(sum(x * x for x in vector_milvus))

    logger.info(f"")
    logger.info(f"📐 [milvus.service.get_embedding]")
    logger.info(f"   向量维度: {len(vector_milvus)}")
    logger.info(f"   向量前 5 个元素: {vector_milvus[:5]}")
    logger.info(f"   L2 范数: {norm_milvus:.10f}  {'✅ ≈ 1.0 (归一化正确)' if abs(norm_milvus - 1.0) < 1e-6 else '❌ != 1.0'}")

    # === 交叉验证：两个归一化实现是否一致 ===
    is_consistent = all(abs(a - b) < 1e-6 for a, b in zip(vector_svc, vector_milvus))
    logger.info(f"")
    logger.info(f"🔗 交叉验证 ('rag_search_service' vs 'milvus.service'):")
    logger.info(f"    {'✅ 两处归一化实现一致' if is_consistent else '❌ 两处归一化实现不一致'}")

    # === 归一化原理说明 ===
    logger.info(f"")
    logger.info(f"{'─' * 60}")
    logger.info(f"📖 归一化原理说明:")
    logger.info(f"   1. Embedding API 返回原始向量 → L2 归一化 (x / ||x||₂)")
    logger.info(f"   2. Milvus 使用 IVF_FLAT 索引 + IP (Inner Product) 度量")
    logger.info(f"   3. 对归一化向量，IP = A·B = cos(θ) × ||A|| × ||B|| = cos(θ)")
    logger.info(f"   4. IP 范围 [-1, 1] → similarity_score = clamp((IP + 1) / 2, 0, 1) → 范围 [0, 1]")
    logger.info(f"   5. 即: similarity_score = (cosine_similarity + 1) / 2")
    logger.info(f"{'─' * 60}")

    return vector_svc, norm_svc


def step4_search_content(rewritten: str) -> list:
    """步骤4: 向量检索 — 展示 Milvus Top-10 结果及相似度分数"""
    print_separator("步骤 4/5: 向量检索 (Milvus Search)")

    logger.info(f"📥 检索关键词: {rewritten}")

    all_results = rag_search_service._search_content(rewritten)
    logger.info(f"📦 检索总数: {len(all_results)}")

    top10 = all_results[:10]

    # 相似度分数统计
    scores = [r.get("similarity_score", 0) for r in top10]
    logger.info("")
    logger.info(f"📊 相似度分数统计 (归一化向量 × IP 度量):")
    logger.info(f"   最高: {max(scores):.4f}  |  最低: {min(scores):.4f}  |  平均: {sum(scores)/len(scores):.4f}")
    logger.info(f"   (IP 距离 → similarity_score = clamp((IP + 1) / 2, 0, 1))")
    logger.info("")
    logger.info(f"📋 返回 Top-10 检索结果:")
    for i, source in enumerate(top10, 1):
        logger.info("")
        sim = source.get("similarity_score", 0)
        bar_len = int(sim * 30)
        bar = "█" * bar_len + "░" * (30 - bar_len)
        logger.info(f"  [{bar}] sim={sim:.4f}  |  结果 {i}/10")
        # 排除 raw_content 避免过长
        display = {k: v for k, v in source.items() if k != "raw_content" and k != "similarity_score"}
        logger.info(json.dumps(display, ensure_ascii=False, indent=4))

    return top10


def putch(text: str, style: str = "normal"):
    """带样式输出到终端（类 DeepSeek/豆包 风格）"""
    styles = {
        "dim":    "\033[2m",    # 思考过程：淡色
        "normal": "\033[0m",    # 最终输出：正常
        "bold":   "\033[1m",    # 标题：加粗
        "cyan":   "\033[36m",   # 信息：青色
        "green":  "\033[32m",   # 成功：绿色
        "yellow": "\033[33m",   # 警告：黄色
    }
    end = styles.get(style, "\033[0m")
    reset = "\033[0m"
    print(f"{end}{text}{reset}", end="", flush=True)


def step5_stream_generation(top10: list):
    """步骤5: 流式生成 — 主流 AI 风格（思考过程 + 最终答案分开展示，实时流式输出）"""
    print_separator("步骤 5/5: 流式生成（类 DeepSeek/豆包 风格）(Streaming Generation)")

    context_text = rag_search_service._format_context(top10)
    logger.info(f"📚 参考上下文长度: {len(context_text)} 字符")

    gen_system = f"""你是一名专业的情报分析师。请根据提供的【参考情报】和【对话上下文】，回答用户的问题。

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
{context_text}

请严格按照上述结构输出回答。

【重要】请使用中文进行思考和推理。思考过程应聚焦于分析逻辑，不得预先撰写完整的最终回答。思考过程应精炼、有条理。"""

    messages = [
        {"role": "system", "content": gen_system},
        {"role": "user", "content": TEST_QUESTION}
    ]

    api_base = llm_settings.API_BASE.rstrip("/")
    url = f"{api_base}/chat/completions"

    payload = {
        "model": llm_settings.MODEL_NAME,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 8192,
        "stream": True,
        "extra_body": {"enable_thinking": True},
    }

    headers = {
        "Authorization": f"Bearer {llm_settings.API_KEY}",
        "Content-Type": "application/json",
    }

    logger.info(f"\n🌐 请求模型: {llm_settings.MODEL_NAME}")
    logger.info(f"🌐 API 端点: {url}")

    full_reasoning = []
    full_content = []
    has_reasoning = False
    has_printed_content_header = False
    started = time.time()
    first_token_time = None
    thinking_token_count = 0
    answer_token_count = 0

    try:
        with httpx.Client(timeout=120.0) as client:
            with client.stream("POST", url, headers=headers, json=payload) as response:
                if response.status_code != 200:
                    logger.error(f"❌ API 请求失败: HTTP {response.status_code}")
                    logger.error(response.text[:500])
                    return

                logger.info(f"✅ API 连接成功 (HTTP 200)")
                logger.info("")

                # ── 思考过程头部（类 DeepSeek 风格） ──
                putch("┌─ 💭 思考过程 (Thinking) ", "cyan")
                putch("────────────────────────────────\n", "dim")
                putch("│ ", "dim")

                for line in response.iter_lines():
                    if not line or not line.startswith("data: "):
                        continue

                    data_str = line[6:]
                    if data_str == "[DONE]":
                        break

                    try:
                        chunk = json.loads(data_str)
                    except json.JSONDecodeError:
                        continue

                    delta = ((chunk.get("choices") or [{}])[0] or {}).get("delta") or {}

                    reasoning_delta = delta.get("reasoning") or ""
                    content_delta = delta.get("content") or ""

                    if not reasoning_delta and not content_delta:
                        reasoning_delta = delta.get("reasoning_content") or ""

                    if reasoning_delta:
                        if not has_reasoning:
                            has_reasoning = True
                            first_token_time = time.time()
                        full_reasoning.append(reasoning_delta)
                        thinking_token_count += 1
                        putch(reasoning_delta, "dim")

                    if content_delta:
                        if has_reasoning and not has_printed_content_header:
                            has_printed_content_header = True
                            # ── 结束思考，切换至最终答案（类 DeepSeek 风格） ──
                            putch("\n")
                            putch("└─ 💭 思考结束", "dim")
                            putch(f" ({thinking_token_count} tokens)", "dim")
                            putch("\n\n")
                            putch("┌─ 📝 最终输出 (Final Answer) ", "bold")
                            putch("───────────────────────────────\n", "normal")
                            putch("│ ", "normal")

                        full_content.append(content_delta)
                        answer_token_count += 1
                        putch(content_delta, "normal")

                elapsed = time.time() - started
                putch("\n")
                putch("└─ 📝 回答结束", "bold")
                putch(f" ({answer_token_count} tokens)\n\n", "normal")

                # ── 完成统计（终端输出 + 日志） ──
                reasoning_full = "".join(full_reasoning)
                content_full = "".join(full_content)
                total_reasoning_len = len(reasoning_full)
                total_content_len = len(content_full)

                # 终端输出统计
                putch("╔═══════════════════════════════════════════╗\n", "cyan")
                putch("║  📊  生成统计                            ║\n", "cyan")
                putch(f"║  ⏱️   总耗时:         {elapsed:>6.2f} 秒            ║\n", "cyan")
                if first_token_time:
                    ttft = first_token_time - started
                    putch(f"║  🏁   首 Token 延迟:  {ttft:>6.2f} 秒            ║\n", "cyan")
                if answer_token_count > 0 and elapsed > 0:
                    speed = answer_token_count / elapsed
                    putch(f"║  ⚡   生成速度:       {speed:>6.2f} tokens/s     ║\n", "cyan")
                putch(f"║  💭   思考过程:       {total_reasoning_len:>6d} 字符 ({thinking_token_count} tokens)  ║\n", "cyan")
                putch(f"║  📝   最终输出:       {total_content_len:>6d} 字符 ({answer_token_count} tokens)  ║\n", "cyan")
                putch("╚═══════════════════════════════════════════╝\n", "cyan")

                # 日志输出统计
                logger.info(f"{'─' * 50}")
                logger.info(f"✅ 流式生成完成!")
                logger.info(f"⏱️  总耗时: {elapsed:.2f} 秒")
                if first_token_time:
                    logger.info(f"🏁  首 Token 延迟: {first_token_time - started:.2f} 秒")
                if answer_token_count > 0 and elapsed > 0:
                    logger.info(f"⚡  生成速度: {answer_token_count / elapsed:.2f} tokens/s")
                logger.info(f"💭  思考过程长度: {total_reasoning_len} 字符 ({thinking_token_count} tokens)")
                logger.info(f"📝  最终输出长度: {total_content_len} 字符 ({answer_token_count} tokens)")
                logger.info(f"{'─' * 50}")

                # 将完整思考过程和最终输出写入日志文件
                logger.info("")
                logger.info("=" * 50)
                logger.info("💭 完整思考过程 (Full Thinking):")
                logger.info("=" * 50)
                logger.info(reasoning_full if reasoning_full else "（模型未返回思考过程）")

                if content_full:
                    logger.info("")
                    logger.info("=" * 50)
                    logger.info("📝 最终输出 (Final Answer):")
                    logger.info("=" * 50)
                    logger.info(content_full)
                else:
                    logger.info("")
                    logger.info("=" * 50)
                    logger.info("📝 最终输出: (模型未返回独立的最终输出)")
                    logger.info("=" * 50)
                    logger.info("（注意：模型将所有内容输出在思考过程中，未生成独立的 content 字段）")

    except httpx.TimeoutException:
        logger.error("❌ API 请求超时 (120s)")
    except httpx.HTTPStatusError as e:
        logger.error(f"❌ HTTP 错误: {e.response.status_code}")
        logger.error(e.response.text[:500])
    except Exception as e:
        logger.error(f"❌ 流式请求失败: {e}", exc_info=True)


def cleanup():
    print_separator("清理: 清除测试会话历史")
    rag_search_service.clear_history(TEST_SESSION_ID)
    logger.info(f"✅ 会话 {TEST_SESSION_ID} 已清除")


def main():
    logger.info("")
    logger.info("#" * 70)
    logger.info(f"#  RAG Search 综合测试")
    logger.info(f"#  模型: {llm_settings.MODEL_NAME}")
    logger.info(f"#  问题: {TEST_QUESTION}")
    logger.info(f"#  日志文件: {log_file}")
    logger.info("#" * 70)
    logger.info("")

    try:
        rewritten = step1_rewrite_question()
        step2_analyze_query(rewritten)
        step3_verify_normalization()
        top10 = step4_search_content(rewritten)
        step5_stream_generation(top10)
    except Exception as e:
        logger.error(f"❌ 测试执行失败: {e}", exc_info=True)
    finally:
        cleanup()
        logger.info("")
        logger.info("#" * 70)
        logger.info(f"#  测试结束")
        logger.info(f"#  日志已保存至: {log_file}")
        logger.info("#" * 70)


if __name__ == "__main__":
    main()
