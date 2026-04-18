from pydantic import BaseModel, Field, model_validator
from typing import Optional, List
from datetime import datetime


class BasicConfig(BaseModel):
    threat_category: List[str] = Field(default_factory=list)
    risk_level: Optional[str] = None
    risk_score: Optional[int] = None
    region: List[str] = Field(default_factory=list)
    industry: List[str] = Field(default_factory=list)


class ASTConfig(BaseModel):
    ast_rules: Optional[dict] = None


class GovernanceConfig(BaseModel):
    dedupe_key: Optional[str] = "不过滤"
    dedupe_window: Optional[int] = 30
    frequency_hour: Optional[int] = 50
    excess: Optional[str] = "静默丢弃"


class DeliveryConfig(BaseModel):
    user_ids: List[str] = Field(default_factory=list)
    group_ids: List[str] = Field(default_factory=list)
    dashboard_enabled: Optional[int] = 1
    webhook_urls: List[str] = Field(default_factory=list)
    telegram_ids: List[str] = Field(default_factory=list)


class MetaConfig(BaseModel):
    charge_person: Optional[str] = None
    priority: Optional[int] = 50
    summary: Optional[str] = None
    visible_scope: Optional[str] = "仅自己"
    editor_ids: List[str] = Field(default_factory=list)


class DWCursor(BaseModel):
    last_time: Optional[int] = None
    last_id: Optional[str] = None


class SubscriptionTopicCreate(BaseModel):
    name: Optional[str] = None
    enabled: Optional[int] = 1
    status: Optional[str] = "active"
    mode: Optional[str] = "basic"

    basic_config: Optional[BasicConfig] = Field(default_factory=BasicConfig)
    ast_config: Optional[ASTConfig] = Field(default_factory=ASTConfig)
    governance: Optional[GovernanceConfig] = Field(default_factory=GovernanceConfig)
    delivery: Optional[DeliveryConfig] = Field(default_factory=DeliveryConfig)
    meta: Optional[MetaConfig] = Field(default_factory=MetaConfig)
    cursor: Optional[DWCursor] = Field(default_factory=DWCursor)

    created_at: Optional[datetime] = None
    last_saved_draft_at: Optional[datetime] = None
    applied_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    final_syn_time: Optional[datetime] = None

    @model_validator(mode="before")
    @classmethod
    def empty_strings_to_none(cls, values):
        datetime_fields = ["created_at", "last_saved_draft_at", "applied_at", "deleted_at", "final_syn_time"]
        for field in datetime_fields:
            if field in values and values[field] == "":
                values[field] = None
        return values

    @model_validator(mode="after")
    def validate_basic_mode(self):
        if self.mode == "basic":
            if not self.basic_config or not self.basic_config.threat_category:
                raise ValueError("basic_config.threat_category 列表不能为空")
            if not self.meta or not self.meta.charge_person:
                raise ValueError("meta.charge_person 字符串不能为空")
        return self


class SubscriptionTopicResponse(BaseModel):
    id: int
    name: Optional[str] = None
    enabled: Optional[int] = 1
    status: Optional[str] = "active"
    mode: Optional[str] = "basic"

    basic_config: Optional[BasicConfig] = Field(default_factory=BasicConfig)
    ast_config: Optional[ASTConfig] = Field(default_factory=ASTConfig)
    governance: Optional[GovernanceConfig] = Field(default_factory=GovernanceConfig)
    delivery: Optional[DeliveryConfig] = Field(default_factory=DeliveryConfig)
    meta: Optional[MetaConfig] = Field(default_factory=MetaConfig)
    cursor: Optional[DWCursor] = Field(default_factory=DWCursor)

    created_at: datetime
    updated_at: datetime
    last_saved_draft_at: Optional[datetime] = None
    applied_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    final_syn_time: Optional[datetime] = None


class SubscriptionTopicListItem(BaseModel):
    id: int
    name: Optional[str] = None
    enabled: Optional[int] = 1
    charge_person: Optional[str] = None
    summary: Optional[str] = None
    final_syn_time: Optional[datetime] = None


SubscriptionTopicPayload = SubscriptionTopicCreate