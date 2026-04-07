from pydantic import BaseModel
from typing import List

class IntelItem(BaseModel):
    id: str
    viewType: str
    title: str
    summary: str
    risk: str
    media: str
    region: str
    topic: str
    date: str
    dayDiff: int
    entities: List[str] = []
    relatedAccounts: List[str] = []