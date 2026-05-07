from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class TimeRangeStat(BaseModel):
    read_count: int = Field(default=0, alias="read_count")
    unread_count: int = Field(default=0, alias="unread_count")

    class Config:
        populate_by_name = True


class SubscriptionAlertStatItem(BaseModel):
    rule_code: Optional[str] = Field(default=None, alias="rule_code")
    rule_name: Optional[str] = Field(default=None, alias="rule_name")
    all_time: TimeRangeStat = Field(default_factory=TimeRangeStat, alias="all_time")
    last_7_days: TimeRangeStat = Field(default_factory=TimeRangeStat, alias="last_7_days")
    last_30_days: TimeRangeStat = Field(default_factory=TimeRangeStat, alias="last_30_days")

    class Config:
        populate_by_name = True


class SubscriptionAlertStatResponse(BaseModel):
    items: List[SubscriptionAlertStatItem]
    total_all_time: TimeRangeStat = Field(default_factory=TimeRangeStat, alias="total_all_time")
    total_last_7_days: TimeRangeStat = Field(default_factory=TimeRangeStat, alias="total_last_7_days")
    total_last_30_days: TimeRangeStat = Field(default_factory=TimeRangeStat, alias="total_last_30_days")


class HourlyCount(BaseModel):
    hour: int = Field(alias="hour")
    count: int = Field(alias="count")

    class Config:
        populate_by_name = True


class SubscriptionTrendItem(BaseModel):
    rule_code: Optional[str] = Field(default=None, alias="rule_code")
    rule_name: Optional[str] = Field(default=None, alias="rule_name")
    today_hourly: List[HourlyCount] = Field(default_factory=list, alias="today_hourly")
    last_12_hours_hourly: List[HourlyCount] = Field(default_factory=list, alias="last_12_hours_hourly")

    class Config:
        populate_by_name = True


class TodayIntelligenceTrendResponse(BaseModel):
    items: List[SubscriptionTrendItem]
    total_today_hourly: List[HourlyCount] = Field(default_factory=list, alias="total_today_hourly")
    total_last_12_hours_hourly: List[HourlyCount] = Field(default_factory=list, alias="total_last_12_hours_hourly")
    current_time: datetime = Field(alias="current_time")