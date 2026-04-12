import time
from typing import Any, Dict

import httpx

from app.config.config import llm_settings


def _build_mock_reply(prompt: str, error: str = "") -> str:
    return (
        "AI模型当前不可用，已返回演示分析结果。\n"
        f"模型: {llm_settings.MODEL_NAME}\n"
        "建议:\n"
        "1) 优先排查高危+跨平台样本\n"
        "2) 对关键词关联账号做链路扩线\n"
        "3) 将命中结果纳入持续监测\n"
        f"\n调试信息: {error or 'N/A'}\n"
        f"\n原始输入摘要: {prompt[:200]}"
    )


def generate_ai_summary(prompt: str, timeout_seconds: float = 30.0) -> Dict[str, Any]:
    """Call OpenAI-compatible chat/completions endpoint and return normalized output."""
    started = time.perf_counter()
    api_base = llm_settings.API_BASE.rstrip("/")
    url = f"{api_base}/chat/completions"

    payload = {
        "model": llm_settings.MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": "你是情报分析助手。请基于输入给出结构化、简洁、可执行的中文研判摘要。"
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        "temperature": 0.2,
        "max_tokens": 900,
    }

    headers = {
        "Authorization": f"Bearer {llm_settings.API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        with httpx.Client(timeout=timeout_seconds) as client:
            response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        content = ""
        choices = data.get("choices") or []
        if choices:
            content = ((choices[0] or {}).get("message") or {}).get("content") or ""

        if not content.strip():
            raise ValueError("empty content from LLM")

        elapsed_ms = int((time.perf_counter() - started) * 1000)
        return {
            "summary": content,
            "model": data.get("model", llm_settings.MODEL_NAME),
            "mock_used": False,
            "elapsed_ms": elapsed_ms,
            "error": "",
            "raw": data,
        }

    except Exception as exc:
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        return {
            "summary": _build_mock_reply(prompt, str(exc)),
            "model": llm_settings.MODEL_NAME,
            "mock_used": True,
            "elapsed_ms": elapsed_ms,
            "error": str(exc),
            "raw": {},
        }
