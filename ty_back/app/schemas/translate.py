from pydantic import BaseModel
from typing import Optional


class TranslateRequest(BaseModel):
    title: str
    content: str
    target_lang: Optional[str] = "简体中文"