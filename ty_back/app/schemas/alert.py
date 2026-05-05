from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class AlertListItem(BaseModel):
    event_id: str = Field(alias="event_id")
    rule_code: Optional[str] = Field(default=None, alias="rule_code")
    rule_name: Optional[str] = Field(default=None, alias="rule_name")
    title: Optional[str] = Field(default=None, alias="title")
    text_preview: Optional[str] = Field(default=None, alias="text_preview")
    author_name: Optional[str] = Field(default=None, alias="author_name")
    platform: Optional[str] = Field(default=None, alias="platform")
    site_name: Optional[str] = Field(default=None, alias="site_name")
    report_time: Optional[datetime] = Field(default=None, alias="report_time")
    severity: Optional[str] = Field(default=None, alias="severity")
    region: Optional[str] = Field(default=None, alias="region")
    topic: Optional[str] = Field(default=None, alias="topic")
    industry: Optional[str] = Field(default=None, alias="industry")
    read_status: Optional[int] = Field(default=None, alias="read_status")
    entity_tags: Optional[List[str]] = Field(default_factory=list, alias="entity_tags")
    content_id: Optional[str] = Field(default=None, alias="content_id")
    false_positive: Optional[int] = Field(default=None, alias="false_positive")
    export_status: Optional[int] = Field(default=None, alias="export_status")
    search_title_text: Optional[str] = Field(default=None, alias="search_title_text")
    media_name: Optional[str] = Field(default=None, alias="media_name")
    threat_category: Optional[str] = Field(default=None, alias="threat_category")
    channel_id: Optional[str] = Field(default=None, alias="channel_id")
    source_handle: Optional[str] = Field(default=None, alias="source_handle")
    source_type: Optional[str] = Field(default=None, alias="source_type")
    entity_values_text: Optional[str] = Field(default=None, alias="entity_values_text")
    is_monitor_target: Optional[int] = Field(default=None, alias="is_monitor_target")

    class Config:
        populate_by_name = True


class AlertDetailResponse(BaseModel):
    title: Optional[str] = None
    author_name: Optional[str] = None
    raw_content: Optional[str] = None


class AlertListResponse(BaseModel):
    items: List[AlertListItem]
    total: int
    page: int
    page_size: int


class RuleNameStatItem(BaseModel):
    rule_name: Optional[str] = Field(default=None, alias="rule_name")
    count: int = Field(default=0, alias="count")

    class Config:
        populate_by_name = True