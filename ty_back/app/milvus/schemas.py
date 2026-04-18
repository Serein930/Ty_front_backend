from typing import Optional
from pydantic import BaseModel


class SyncRequest(BaseModel):
    content_id: Optional[str] = None
    batch_size: int = 100
    limit: int = 1000


class SyncResponse(BaseModel):
    synced_count: int
    total_available: int
    message: str
