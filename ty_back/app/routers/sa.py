from datetime import datetime, timedelta
from fastapi import APIRouter

from app.schemas.base import Result
from app.schemas.sa import (
    SubscriptionAlertStatItem,
    SubscriptionAlertStatResponse,
    TimeRangeStat,
    SubscriptionTrendItem,
    TodayIntelligenceTrendResponse,
    HourlyCount,
)
from app.utils.ch_client import execute_ch_query
from app.config.config import ch_settings

router = APIRouter(prefix="/api/sa", tags=["态势感知"])

ALERT_TABLE_NAME = f"{ch_settings.DATABASE}.hawkeye_ads_alert_event_latest"


@router.get("/subscription/alert/stats", response_model=Result[SubscriptionAlertStatResponse])
async def get_subscription_alert_stats():
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    days_ago_7 = (today_start - timedelta(days=6)).strftime("%Y-%m-%d")
    days_ago_30 = (today_start - timedelta(days=29)).strftime("%Y-%m-%d")
    today_str = today_start.strftime("%Y-%m-%d")

    query = f"""
    SELECT
        rule_code,
        rule_name,
        sum(if(read_status = 1, 1, 0)) as all_read,
        sum(if(read_status != 1 or read_status IS NULL, 1, 0)) as all_unread,
        sum(if(read_status = 1 AND report_time >= '{days_ago_7}', 1, 0)) as read_7d,
        sum(if((read_status != 1 OR read_status IS NULL) AND report_time >= '{days_ago_7}', 1, 0)) as unread_7d,
        sum(if(read_status = 1 AND report_time >= '{days_ago_30}', 1, 0)) as read_30d,
        sum(if((read_status != 1 OR read_status IS NULL) AND report_time >= '{days_ago_30}', 1, 0)) as unread_30d
    FROM {ALERT_TABLE_NAME}
    WHERE false_positive != 1
    GROUP BY rule_code, rule_name
    ORDER BY all_unread DESC
    """

    result = await execute_ch_query(query)

    items = []
    total_all_read = 0
    total_all_unread = 0
    total_7d_read = 0
    total_7d_unread = 0
    total_30d_read = 0
    total_30d_unread = 0

    for row in result.get("data", []):
        all_read = int(row.get("all_read", 0) or 0)
        all_unread = int(row.get("all_unread", 0) or 0)
        read_7d = int(row.get("read_7d", 0) or 0)
        unread_7d = int(row.get("unread_7d", 0) or 0)
        read_30d = int(row.get("read_30d", 0) or 0)
        unread_30d = int(row.get("unread_30d", 0) or 0)

        total_all_read += all_read
        total_all_unread += all_unread
        total_7d_read += read_7d
        total_7d_unread += unread_7d
        total_30d_read += read_30d
        total_30d_unread += unread_30d

        items.append(SubscriptionAlertStatItem(
            rule_code=row.get("rule_code"),
            rule_name=row.get("rule_name"),
            all_time=TimeRangeStat(read_count=all_read, unread_count=all_unread),
            last_7_days=TimeRangeStat(read_count=read_7d, unread_count=unread_7d),
            last_30_days=TimeRangeStat(read_count=read_30d, unread_count=unread_30d),
        ))

    return Result.success(data=SubscriptionAlertStatResponse(
        items=items,
        total_all_time=TimeRangeStat(read_count=total_all_read, unread_count=total_all_unread),
        total_last_7_days=TimeRangeStat(read_count=total_7d_read, unread_count=total_7d_unread),
        total_last_30_days=TimeRangeStat(read_count=total_30d_read, unread_count=total_30d_unread),
    ))


@router.get("/intelligence/trend", response_model=Result[TodayIntelligenceTrendResponse])
async def get_today_intelligence_trend():
    time_query = f"""
    SELECT
        now() as current_time,
        toStartOfDay(now()) as today_start,
        toHour(now()) as current_hour,
        toHour(toStartOfDay(now()) + interval (toHour(now()) + 1) hour) as current_hour_ceiling,
        toStartOfDay(now()) + interval (toHour(now()) + 1) hour as today_end
    """
    time_result = await execute_ch_query(time_query)
    time_row = time_result.get("data", [{}])[0]

    current_time_str = time_row.get("current_time")
    today_start_str = time_row.get("today_start")
    current_hour_ceiling = int(time_row.get("current_hour_ceiling", 0))

    hours_12_range = []
    hours_12_start = current_hour_ceiling - 12
    if hours_12_start < 0:
        hours_12_range = list(range(0, current_hour_ceiling + 1))
    else:
        hours_12_range = [(hours_12_start + i) % 24 for i in range(12)]

    subscriptions_query = f"""
    SELECT DISTINCT rule_code, rule_name
    FROM {ALERT_TABLE_NAME}
    WHERE rule_code IS NOT NULL AND rule_code != ''
    ORDER BY rule_code
    """

    subscriptions_result = await execute_ch_query(subscriptions_query)

    items_dict = {}
    for row in subscriptions_result.get("data", []):
        rule_code = row.get("rule_code")
        rule_name = row.get("rule_name")
        items_dict[rule_code] = {
            "rule_code": rule_code,
            "rule_name": rule_name,
            "today_hourly": [HourlyCount(hour=h, count=0) for h in range(24)],
            "last_12_hours_hourly": [HourlyCount(hour=h, count=0) for h in hours_12_range],
        }

    today_end_str = time_row.get("today_end")

    trend_query = f"""
    SELECT
        rule_code,
        rule_name,
        toHour(report_time) as hour,
        count() as cnt
    FROM {ALERT_TABLE_NAME}
    WHERE report_time >= '{today_start_str}' AND report_time < '{today_end_str}'
    GROUP BY rule_code, rule_name, toHour(report_time)
    ORDER BY rule_code, hour
    """

    trend_result = await execute_ch_query(trend_query)

    total_today_hourly = [HourlyCount(hour=h, count=0) for h in range(24)]
    total_12h_hourly = [HourlyCount(hour=h, count=0) for h in hours_12_range]

    for row in trend_result.get("data", []):
        rule_code = row.get("rule_code")
        hour = int(row.get("hour", 0))
        cnt = int(row.get("cnt", 0) or 0)

        if rule_code in items_dict:
            items_dict[rule_code]["today_hourly"][hour].count += cnt
            total_today_hourly[hour].count += cnt

            idx = hours_12_range.index(hour) if hour in hours_12_range else -1
            if idx >= 0:
                items_dict[rule_code]["last_12_hours_hourly"][idx].count += cnt
                total_12h_hourly[idx].count += cnt

    items = [
        SubscriptionTrendItem(
            rule_code=data["rule_code"],
            rule_name=data["rule_name"],
            today_hourly=data["today_hourly"],
            last_12_hours_hourly=data["last_12_hours_hourly"],
        )
        for data in items_dict.values()
    ]

    current_time = datetime.fromisoformat(current_time_str.replace(" ", "T")) if current_time_str else datetime.now()

    return Result.success(data=TodayIntelligenceTrendResponse(
        items=items,
        total_today_hourly=total_today_hourly,
        total_last_12_hours_hourly=total_12h_hourly,
        current_time=current_time,
    ))