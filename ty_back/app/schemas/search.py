# app/schemas/search.py
from pydantic import BaseModel
from typing import List, Optional

class SearchTabCount(BaseModel):
    doc_type: str
    total_count: int

class SearchResultItem(BaseModel):
    doc_type: str
    doc_id: str
    event_date: str
    platform: str
    title: str
    text_preview: str
    category_label: str
    threat_category: str
    severity: str
    primary_handle: str

class SearchResponse(BaseModel):
    tabs: List[SearchTabCount]
    items: List[SearchResultItem]