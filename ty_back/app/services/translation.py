import re
import json
from typing import Optional, Generator
import httpx
from app.config.config import llm_settings


class TranslationService:
    _instance: Optional["TranslationService"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.api_base = llm_settings.API_BASE
        self.api_key = llm_settings.API_KEY
        self.model_name = llm_settings.MODEL_NAME

    def _load_prompt(self, prompt_key: str) -> str:
        prompts_file = __file__.rsplit("/", 1)[0].rsplit("/", 1)[0] + "/config/prompts.json"
        with open(prompts_file, "r", encoding="utf-8") as f:
            prompts = json.load(f)
        return prompts.get(prompt_key, {}).get("system_prompt", "")

    def _filter_thinking_tags(self, text: str) -> str:
        pattern = r"<think>.*?</think>"
        return re.sub(pattern, "", text, flags=re.DOTALL).strip()

    def translate(self, title: str, content: str, target_lang: str = "简体中文") -> str:
        if title and title.strip():
            full_content = f"标题：{title}\n正文：{content}"
        else:
            full_content = content
        system_prompt = self._load_prompt("translation")
        system_prompt = system_prompt.format(target_lang=target_lang, content=full_content)

        user_prompt = f"请翻译以下内容为{target_lang}，直接输出翻译结果，不要任何解释：\n\n{full_content}"

        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.1,
            "max_tokens": 2000
        }

        url = f"{self.api_base}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        with httpx.Client(timeout=60.0) as client:
            response = client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
            content_text = result["choices"][0]["message"]["content"]
            return self._filter_thinking_tags(content_text)

    def translate_stream(self, title: str, content: str, target_lang: str = "简体中文") -> Generator[str, None, None]:
        if title and title.strip():
            full_content = f"标题：{title}\n正文：{content}"
        else:
            full_content = content
        system_prompt = self._load_prompt("translation")
        system_prompt = system_prompt.format(target_lang=target_lang, content=full_content)

        user_prompt = f"请翻译以下内容为{target_lang}，直接输出翻译结果，不要任何解释：\n\n{full_content}"

        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.1,
            "max_tokens": 2000,
            "stream": True
        }

        url = f"{self.api_base}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        buffer = ""
        with httpx.Client(timeout=60.0) as client:
            with client.stream("POST", url, json=payload, headers=headers) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str == "[DONE]":
                            break
                        try:
                            data = json.loads(data_str)
                            delta = data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                            if delta:
                                buffer += delta
                                yield self._filter_thinking_tags(buffer)
                        except json.JSONDecodeError:
                            continue


translation_service = TranslationService()