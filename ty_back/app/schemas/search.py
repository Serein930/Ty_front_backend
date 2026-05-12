# app/schemas/search.py
from pydantic import BaseModel
from typing import List, Optional

class SearchTabCount(BaseModel):
    doc_type: str
    total_count: int

class SearchResultItem(BaseModel):
    id: str
    viewType: str
    title: str
    summary: str
    risk: str
    media: str
    region: str
    region_province: str
    topic: str
    date: str
    dayDiff: int
    entities: List[str] = []
    relatedAccounts: List[str] = []

class SearchResponse(BaseModel):
    tabs: List[SearchTabCount]
    items: List[SearchResultItem]