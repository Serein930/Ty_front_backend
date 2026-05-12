import json
from datetime import datetime
from typing import Any, List, Literal

from fastapi import APIRouter, HTTPException, Path as PathParam, Query, Body

from app.schemas.topic import SubscriptionTopicCreate, SubscriptionTopicResponse, SubscriptionTopicListItem, TopicIdNameItem, SubscriptionTopicSearchRequest
from app.schemas.topic import RuleSaveRequest, HistoryRecordItem
from app.schemas.alert import AlertListItem, AlertListResponse, AlertDetailResponse, RuleNameStatItem
from app.schemas.base import Result
from app.utils.ch_client import execute_ch_query
from app.config.config import ch_settings

router = APIRouter(prefix="/api/topics", tags=["专题管理"])

DATABASE = ch_settings.DATABASE
TABLE_NAME = f"{DATABASE}.subscription_topics"
HISTORY_TABLE_NAME = f"{DATABASE}.subscription_topics_history"
ALERT_TABLE_NAME = "hawkeye_test.hawkeye_ads_alert_event_latest"
ALERT_STATUS_TABLE_NAME = "hawkeye_test.hawkeye_dwd_alert_event_status"
CONTENT_TABLE_NAME = "hawkeye_test.hawkeye_dwd_intel_content_cold"


SaveAction = Literal["save_draft", "apply"]


def _escape_sql_string(s: str) -> str:
    return s.replace("'", "''")


def _serialize_json_field(value: Any) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, str):
        return f"'{_escape_sql_string(value)}'"
    return f"'{_escape_sql_string(json.dumps(value, ensure_ascii=False))}'"


def _format_datetime(dt: datetime) -> str:
    if dt is None:
        return "NULL"
    return f"'{dt.strftime('%Y-%m-%d %H:%M:%S')}'"


@router.post("/create", response_model=Result[SubscriptionTopicResponse])
async def create_topic(payload: SubscriptionTopicCreate):
    rule_code = str(int(datetime.now().timestamp() * 1000))
    now = datetime.now()

    if payload.created_at is None:
        created_at = now
    else:
        created_at = payload.created_at

    topic_data = payload.model_dump(mode="json")

    basic_config_json = json.dumps(topic_data.get("basic_config") or {}, ensure_ascii=False)
    ast_config_json = json.dumps(topic_data.get("ast_config") or {}, ensure_ascii=False)
    governance_json = json.dumps(topic_data.get("governance") or {}, ensure_ascii=False)
    delivery_json = json.dumps(topic_data.get("delivery") or {}, ensure_ascii=False)
    meta_json = json.dumps(topic_data.get("meta") or {}, ensure_ascii=False)

    query = f"""
    INSERT INTO {TABLE_NAME} (
        rule_code, rule_name, enabled, status, mode,
        basic_config, ast_config, governance, delivery, meta,
        created_at, updated_at, last_saved_draft_at, applied_at, deleted_at, final_syn_time
    ) VALUES (
        '{rule_code}',
        {_serialize_json_field(topic_data.get("rule_name"))},
        {topic_data.get("enabled", 1)},
        '{topic_data.get("status", "draft")}',
        '{topic_data.get("mode", "basic")}',
        '{_escape_sql_string(basic_config_json)}',
        '{_escape_sql_string(ast_config_json)}',
        '{_escape_sql_string(governance_json)}',
        '{_escape_sql_string(delivery_json)}',
        '{_escape_sql_string(meta_json)}',
        {_format_datetime(created_at)},
        {_format_datetime(now)},
        {_format_datetime(now)},
        {_format_datetime(now)},
        NULL,
        NULL
    )
    """

    await execute_ch_query(query)

    response_data = {
        "rule_code": rule_code,
        "rule_name": topic_data.get("rule_name"),
        "enabled": topic_data.get("enabled", 1),
        "status": topic_data.get("status", "draft"),
        "mode": topic_data.get("mode", "basic"),
        "basic_config": topic_data.get("basic_config") or {},
        "ast_config": topic_data.get("ast_config") or {},
        "governance": topic_data.get("governance") or {},
        "delivery": topic_data.get("delivery") or {},
        "meta": topic_data.get("meta") or {},
        "created_at": created_at,
        "updated_at": now,
    }

    return Result.success(data=SubscriptionTopicResponse(**response_data))


@router.get("/list", response_model=Result[list[SubscriptionTopicListItem]])
async def list_topics():
    query = f"""
    SELECT 
        rule_code, 
        rule_name, 
        enabled, 
        status,
        JSONExtractString(meta, 'charge_person') AS charge_person,
        JSONExtractString(meta, 'summary') AS summary,
        final_syn_time
    FROM {TABLE_NAME}
    ORDER BY created_at DESC
    """

    result = await execute_ch_query(query)
    items = []
    for row in result.get("data", []):
        items.append(
            SubscriptionTopicListItem(
                rule_code=row.get("rule_code", ""),
                rule_name=row.get("rule_name"),
                enabled=row.get("enabled", 1),
                status=row.get("status"),
                charge_person=row.get("charge_person"),
                summary=row.get("summary"),
                final_syn_time=row.get("final_syn_time"),
            )
        )

    return Result.success(data=items)


@router.get("/names", response_model=Result[list[TopicIdNameItem]])
async def list_topic_names():
    query = f"""
    SELECT rule_code, rule_name
    FROM {TABLE_NAME}
    WHERE deleted_at IS NULL
    ORDER BY created_at DESC
    """

    result = await execute_ch_query(query)
    items = []
    for row in result.get("data", []):
        items.append(
            TopicIdNameItem(
                rule_code=row.get("rule_code", ""),
                rule_name=row.get("rule_name", ""),
            )
        )

    return Result.success(data=items)


@router.post("/search", response_model=Result[list[SubscriptionTopicResponse]])
async def search_topics(payload: SubscriptionTopicSearchRequest):
    keyword = payload.keyword.strip()

    escaped_keyword = _escape_sql_string(keyword)
    like_pattern = f"%{escaped_keyword}%"

    if keyword:
        query = f"""
        SELECT
            rule_code, rule_name, enabled, status, mode,
            basic_config, ast_config, governance, delivery, meta,
            created_at, updated_at, last_saved_draft_at, applied_at, deleted_at, final_syn_time
        FROM {TABLE_NAME}
        WHERE deleted_at IS NULL
          AND (
            rule_name LIKE '{like_pattern}'
            OR JSONExtractString(meta, 'charge_person') LIKE '{like_pattern}'
            OR basic_config LIKE '{like_pattern}'
            OR ast_config LIKE '{like_pattern}'
            OR delivery LIKE '{like_pattern}'
          )
        ORDER BY created_at DESC
        """
    else:
        query = f"""
        SELECT
            rule_code, rule_name, enabled, status, mode,
            basic_config, ast_config, governance, delivery, meta,
            created_at, updated_at, last_saved_draft_at, applied_at, deleted_at, final_syn_time
        FROM {TABLE_NAME}
        WHERE deleted_at IS NULL
        ORDER BY created_at DESC
        """

    result = await execute_ch_query(query)
    items = []
    for row in result.get("data", []):
        basic_config_str = row.get("basic_config", "{}")
        ast_config_str = row.get("ast_config", "{}")
        governance_str = row.get("governance", "{}")
        delivery_str = row.get("delivery", "{}")
        meta_str = row.get("meta", "{}")

        try:
            basic_config = json.loads(basic_config_str) if basic_config_str else {}
            ast_config = json.loads(ast_config_str) if ast_config_str else {}
            governance = json.loads(governance_str) if governance_str else {}
            delivery = json.loads(delivery_str) if delivery_str else {}
            meta = json.loads(meta_str) if meta_str else {}
        except json.JSONDecodeError:
            basic_config = {}
            ast_config = {}
            governance = {}
            delivery = {}
            meta = {}

        items.append(
            SubscriptionTopicResponse(
                rule_code=row.get("rule_code", ""),
                rule_name=row.get("rule_name"),
                enabled=row.get("enabled", 1),
                status=row.get("status"),
                mode=row.get("mode"),
                basic_config=basic_config,
                ast_config=ast_config,
                governance=governance,
                delivery=delivery,
                meta=meta,
                created_at=row.get("created_at"),
                updated_at=row.get("updated_at"),
                last_saved_draft_at=row.get("last_saved_draft_at"),
                applied_at=row.get("applied_at"),
                deleted_at=row.get("deleted_at"),
                final_syn_time=row.get("final_syn_time"),
            )
        )

    return Result.success(data=items)


@router.get("/{rule_code}/config", response_model=Result[dict])
async def get_topic_config(rule_code: str = PathParam(..., description="专题CODE")):
    print(f"\n{'='*60}")
    print(f"[GET TOPIC CONFIG] Getting config for rule_code={rule_code}")
    print(f"{'='*60}")

    query = f"""
    SELECT rule_code, rule_name, enabled, status, mode,
           basic_config, ast_config, governance, delivery, meta,
           created_at, updated_at, last_saved_draft_at, applied_at, deleted_at, final_syn_time
    FROM {TABLE_NAME}
    WHERE rule_code = '{_escape_sql_string(rule_code)}' AND deleted_at IS NULL
    """

    result = await execute_ch_query(query)
    data = result.get("data", [])

    if not data:
        raise HTTPException(status_code=404, detail=f"专题 {rule_code} 不存在")

    row = data[0]

    basic_config_str = row.get("basic_config", "{}")
    ast_config_str = row.get("ast_config", "{}")
    governance_str = row.get("governance", "{}")
    delivery_str = row.get("delivery", "{}")
    meta_str = row.get("meta", "{}")

    try:
        basic_config = json.loads(basic_config_str) if basic_config_str else {}
        ast_config = json.loads(ast_config_str) if ast_config_str else {}
        governance = json.loads(governance_str) if governance_str else {}
        delivery = json.loads(delivery_str) if delivery_str else {}
        meta = json.loads(meta_str) if meta_str else {}
    except json.JSONDecodeError:
        basic_config = {}
        ast_config = {}
        governance = {}
        delivery = {}
        meta = {}

    topic_data = {
        "rule_code": row.get("rule_code"),
        "rule_name": row.get("rule_name"),
        "enabled": row.get("enabled"),
        "status": row.get("status"),
        "mode": row.get("mode"),
        "basic_config": basic_config,
        "ast_config": ast_config,
        "governance": governance,
        "delivery": delivery,
        "meta": meta,
        "created_at": row.get("created_at"),
        "updated_at": row.get("updated_at"),
        "last_saved_draft_at": row.get("last_saved_draft_at"),
        "applied_at": row.get("applied_at"),
        "deleted_at": row.get("deleted_at"),
        "final_syn_time": row.get("final_syn_time"),
    }

    print(f"[GET TOPIC CONFIG] Returning config for rule_code={rule_code}")
    print(f"{'='*60}\n")

    return Result.success(data={
        "rule_code": rule_code,
        "config": topic_data
    })


@router.patch("/{rule_code}/toggle", response_model=Result[dict])
async def toggle_topic(
    rule_code: str = PathParam(..., description="专题CODE"),
    payload: dict = Body(..., description="启用/禁用状态"),
):
    enabled = payload.get("enabled")
    if enabled is None:
        raise HTTPException(status_code=400, detail="enabled 参数必填")

    if enabled:
        query = f"""
        ALTER TABLE {TABLE_NAME} UPDATE enabled = 1
        WHERE rule_code = '{_escape_sql_string(rule_code)}'
        """
        message = "专题已启用"
    else:
        query = f"""
        ALTER TABLE {TABLE_NAME} UPDATE enabled = 0
        WHERE rule_code = '{_escape_sql_string(rule_code)}'
        """
        message = "专题已停用"

    await execute_ch_query(query)

    return Result.success(data={"rule_code": rule_code, "enabled": int(enabled), "message": message})


@router.delete("/{rule_code}", response_model=Result[dict])
async def delete_topic(
    rule_code: str = PathParam(..., description="规则CODE"),
):
    now = datetime.now()

    check_query = f"""
    SELECT rule_code FROM {TABLE_NAME}
    WHERE rule_code = '{_escape_sql_string(rule_code)}' AND deleted_at IS NULL
    """

    check_result = await execute_ch_query(check_query)
    existing = check_result.get("data", [])

    if not existing:
        raise HTTPException(status_code=404, detail=f"规则 {rule_code} 不存在或已删除")

    delete_query = f"""
    ALTER TABLE {TABLE_NAME} UPDATE deleted_at = {_format_datetime(now)}
    WHERE rule_code = '{_escape_sql_string(rule_code)}'
    """
    await execute_ch_query(delete_query)

    return Result.success(data={"rule_code": rule_code, "deleted_at": now.isoformat()})


@router.get("/alert/list_all", response_model=Result[list[AlertListItem]])
async def list_alerts_all():
    data_query = f"""
    SELECT
        event_id, rule_code, rule_name, title, text_preview, author_name,
        platform, site_name, report_time, severity, region, topic, industry,
        read_status, entity_tags, content_id, false_positive, export_status,
        search_title_text, media_name, threat_category, channel_id,
        source_handle, source_type, entity_values_text
    FROM {ALERT_TABLE_NAME}
    WHERE false_positive != 1
    ORDER BY report_time DESC
    """

    result = await execute_ch_query(data_query)
    items = _parse_alert_items(result.get("data", []))

    return Result.success(data=items, msg=f"共 {len(items)} 条")


@router.get("/alert/list", response_model=Result[list[AlertListItem]])
async def list_alerts_by_threat_category(
    threat_category: str = Query(..., description="威胁分类"),
):
    data_query = f"""
    SELECT
        event_id, rule_code, rule_name, title, text_preview, author_name,
        platform, site_name, report_time, severity, region, topic, industry,
        read_status, entity_tags, content_id, false_positive, export_status,
        search_title_text, media_name, threat_category, channel_id,
        source_handle, source_type, entity_values_text
    FROM {ALERT_TABLE_NAME}
    WHERE threat_category = '{_escape_sql_string(threat_category)}' AND false_positive != 1
    ORDER BY report_time DESC
    """

    result = await execute_ch_query(data_query)
    items = _parse_alert_items(result.get("data", []))

    return Result.success(data=items, msg=f"共 {len(items)} 条")


@router.get("/alert/list_by_topic_name", response_model=Result[list[AlertListItem]])
async def list_alerts_by_topic_name(
    name: str = Query(..., description="订阅名称（规则名称）"),
):
    data_query = f"""
    SELECT
        event_id, rule_code, rule_name, title, text_preview, author_name,
        platform, site_name, report_time, severity, region, topic, industry,
        read_status, entity_tags, content_id, false_positive, export_status,
        search_title_text, media_name, threat_category, channel_id,
        source_handle, source_type, entity_values_text
    FROM {ALERT_TABLE_NAME}
    WHERE rule_name = '{_escape_sql_string(name)}' AND false_positive != 1
    ORDER BY report_time DESC
    """

    result = await execute_ch_query(data_query)
    items = _parse_alert_items(result.get("data", []))

    return Result.success(data=items, msg=f"共 {len(items)} 条")


@router.get("/alert/rule_name_stats", response_model=Result[List[RuleNameStatItem]])
async def get_rule_name_stats():
    query = f"""
    SELECT rule_name, count() as count
    FROM {ALERT_TABLE_NAME}
    WHERE false_positive != 1
    GROUP BY rule_name
    ORDER BY count DESC
    LIMIT 5
    """

    result = await execute_ch_query(query)
    items = []
    for row in result.get("data", []):
        items.append(
            RuleNameStatItem(
                rule_name=row.get("rule_name", ""),
                count=row.get("count", 0),
            )
        )

    return Result.success(data=items, msg=f"共 {len(items)} 条")


def _parse_alert_items(data: list) -> List[AlertListItem]:
    from app.schemas.alert import AlertListItem
    items = []
    for row in data:
        items.append(
            AlertListItem(
                event_id=row.get("event_id", ""),
                rule_code=row.get("rule_code", ""),
                rule_name=row.get("rule_name", ""),
                title=row.get("title"),
                text_preview=row.get("text_preview"),
                author_name=row.get("author_name"),
                platform=row.get("platform"),
                site_name=row.get("site_name"),
                report_time=row.get("report_time"),
                severity=row.get("severity"),
                region=row.get("region"),
                topic=row.get("topic"),
                industry=row.get("industry"),
                read_status=row.get("read_status"),
                entity_tags=row.get("entity_tags", []),
                content_id=row.get("content_id"),
                false_positive=row.get("false_positive"),
                export_status=row.get("export_status"),
                search_title_text=row.get("search_title_text"),
                media_name=row.get("media_name"),
                threat_category=row.get("threat_category"),
                channel_id=row.get("channel_id"),
                source_handle=row.get("source_handle"),
                source_type=row.get("source_type"),
                entity_values_text=row.get("entity_values_text"),
                is_monitor_target=row.get("is_monitor_target"),
            )
        )
    return items


@router.post("/alert/{event_id}/toggle_read", response_model=Result[dict])
async def toggle_alert_read(event_id: str = PathParam(..., description="告警事件ID")):
    now = datetime.now()

    check_query = f"""
    SELECT read_status
    FROM {ALERT_TABLE_NAME}
    WHERE event_id = '{_escape_sql_string(event_id)}'
    """

    result = await execute_ch_query(check_query)
    data = result.get("data", [])

    if not data:
        raise HTTPException(status_code=404, detail=f"告警事件 {event_id} 不存在")

    current_status = data[0].get("read_status", 0)
    new_status = 1 if current_status == 0 else 0

    update_query = f"""
    ALTER TABLE {ALERT_TABLE_NAME} UPDATE read_status = {new_status}
    WHERE event_id = '{_escape_sql_string(event_id)}'
    """

    await execute_ch_query(update_query)

    status_update_query = f"""
    ALTER TABLE {ALERT_STATUS_TABLE_NAME} UPDATE read_status = {new_status}
    WHERE event_id = '{_escape_sql_string(event_id)}'
    """

    await execute_ch_query(status_update_query)

    return Result.success(data={"event_id": event_id, "read_status": new_status}, msg="已读状态已更新")


@router.get("/alert/{event_id}/detail", response_model=Result[AlertDetailResponse])
async def get_alert_detail(
    event_id: str = PathParam(..., description="告警事件ID"),
    content_id: str = Query(..., description="内容ID（用于查询原文正文）"),
):
    alert_query = f"""
    SELECT title, author_name
    FROM {ALERT_TABLE_NAME}
    WHERE event_id = '{_escape_sql_string(event_id)}'
    """

    alert_result = await execute_ch_query(alert_query)
    alert_data = alert_result.get("data", [])

    if not alert_data:
        raise HTTPException(status_code=404, detail=f"告警事件 {event_id} 不存在")

    alert_row = alert_data[0]

    content_query = f"""
    SELECT raw_content
    FROM {CONTENT_TABLE_NAME}
    WHERE content_id = '{_escape_sql_string(content_id)}'
    """

    content_result = await execute_ch_query(content_query)
    content_data = content_result.get("data", [])
    raw_content = content_data[0].get("raw_content") if content_data else None

    from app.schemas.alert import AlertDetailResponse
    return Result.success(data=AlertDetailResponse(
        title=alert_row.get("title"),
        author_name=alert_row.get("author_name"),
        raw_content=raw_content,
    ))


@router.post("/alert/{event_id}/export", response_model=Result[dict])
async def mark_export_status(
    event_id: str = PathParam(..., description="告警事件ID"),
):
    check_query = f"""
    SELECT event_id FROM {ALERT_TABLE_NAME} WHERE event_id = '{_escape_sql_string(event_id)}'
    """
    check_result = await execute_ch_query(check_query)
    if not check_result.get("data", []):
        raise HTTPException(status_code=404, detail=f"告警事件 {event_id} 不存在")

    update_query = f"""
    ALTER TABLE {ALERT_TABLE_NAME} UPDATE export_status = 1
    WHERE event_id = '{_escape_sql_string(event_id)}'
    """
    await execute_ch_query(update_query)

    status_update_query = f"""
    ALTER TABLE {ALERT_STATUS_TABLE_NAME} UPDATE export_status = 1
    WHERE event_id = '{_escape_sql_string(event_id)}'
    """
    await execute_ch_query(status_update_query)

    return Result.success(data={"event_id": event_id, "export_status": 1}, msg="导出状态已更新")


@router.post("/alert/{event_id}/false_positive", response_model=Result[dict])
async def mark_false_positive(
    event_id: str = PathParam(..., description="告警事件ID"),
):
    now = datetime.now()

    update_query = f"""
    ALTER TABLE {ALERT_TABLE_NAME} UPDATE false_positive = 1
    WHERE event_id = '{_escape_sql_string(event_id)}'
    """

    await execute_ch_query(update_query)

    status_update_query = f"""
    ALTER TABLE {ALERT_STATUS_TABLE_NAME} UPDATE false_positive = 1
    WHERE event_id = '{_escape_sql_string(event_id)}'
    """

    await execute_ch_query(status_update_query)

    return Result.success(data={"event_id": event_id, "false_positive": 1}, msg="误报标记成功")


@router.post("/", response_model=Result[SubscriptionTopicResponse])
async def save_or_apply_rule(
    payload: RuleSaveRequest,
    action: SaveAction = Query(..., description="操作类型: save_draft-保存草稿, apply-发布规则")
):
    now = datetime.now()

    rule_code = payload.rule_id.strip() if payload.rule_id and payload.rule_id.strip() else None
    if not rule_code:
        rule_code = str(int(now.timestamp() * 1000))

    payload.rule_id = rule_code

    basic_config_json = json.dumps(payload.basic_config or {}, ensure_ascii=False)
    ast_config_json = json.dumps(payload.ast_config or {}, ensure_ascii=False)
    governance_json = json.dumps(payload.governance or {}, ensure_ascii=False)
    delivery_json = json.dumps(payload.delivery or {}, ensure_ascii=False)
    meta_json = json.dumps(payload.meta or {}, ensure_ascii=False)

    if action == "apply":
        status_value = "applied"
        applied_at_value = _format_datetime(now)
        last_saved_draft_at_value = "NULL"
    else:
        status_value = "draft"
        applied_at_value = "NULL"
        last_saved_draft_at_value = _format_datetime(now)

    check_query = f"""
    SELECT rule_code, rule_name, enabled, status, mode,
           basic_config, ast_config, governance, delivery, meta,
           created_at, updated_at, last_saved_draft_at, applied_at
    FROM {TABLE_NAME}
    WHERE rule_code = '{_escape_sql_string(rule_code)}' AND deleted_at IS NULL
    """

    check_result = await execute_ch_query(check_query)
    existing = check_result.get("data", [])

    if existing:
        old_row = existing[0]
        old_basic_config_str = old_row.get("basic_config", "{}")
        old_ast_config_str = old_row.get("ast_config", "{}")
        old_governance_str = old_row.get("governance", "{}")
        old_delivery_str = old_row.get("delivery", "{}")
        old_meta_str = old_row.get("meta", "{}")

        try:
            old_basic_config = json.loads(old_basic_config_str) if old_basic_config_str else {}
            old_ast_config = json.loads(old_ast_config_str) if old_ast_config_str else {}
            old_governance = json.loads(old_governance_str) if old_governance_str else {}
            old_delivery = json.loads(old_delivery_str) if old_delivery_str else {}
            old_meta = json.loads(old_meta_str) if old_meta_str else {}
        except json.JSONDecodeError:
            old_basic_config = {}
            old_ast_config = {}
            old_governance = {}
            old_delivery = {}
            old_meta = {}

        old_snapshot_dict = {
            "rule_code": old_row.get("rule_code"),
            "rule_name": old_row.get("rule_name"),
            "enabled": old_row.get("enabled"),
            "status": old_row.get("status"),
            "mode": old_row.get("mode"),
            "basic_config": old_basic_config,
            "ast_config": old_ast_config,
            "governance": old_governance,
            "delivery": old_delivery,
            "meta": old_meta,
        }
        old_snapshot_json = json.dumps(old_snapshot_dict, ensure_ascii=False)

        history_insert_query = f"""
        INSERT INTO {HISTORY_TABLE_NAME} (
            rule_code, action, operator, snapshot_data, created_at
        ) VALUES (
            '{_escape_sql_string(rule_code)}',
            '{action}',
            'system',
            '{_escape_sql_string(old_snapshot_json)}',
            {_format_datetime(now)}
        )
        """
        await execute_ch_query(history_insert_query)

        delete_query = f"""
        ALTER TABLE {TABLE_NAME} DELETE WHERE rule_code = '{_escape_sql_string(rule_code)}'
        """
        await execute_ch_query(delete_query)

        insert_query = f"""
        INSERT INTO {TABLE_NAME} (
            rule_code, rule_name, enabled, status, mode,
            basic_config, ast_config, governance, delivery, meta,
            created_at, updated_at, last_saved_draft_at, applied_at
        ) VALUES (
            '{_escape_sql_string(rule_code)}',
            {_serialize_json_field(payload.rule_name)},
            {payload.enabled.value if hasattr(payload.enabled, 'value') else payload.enabled},
            '{status_value}',
            '{payload.mode.value if hasattr(payload.mode, 'value') else payload.mode}',
            '{_escape_sql_string(basic_config_json)}',
            '{_escape_sql_string(ast_config_json)}',
            '{_escape_sql_string(governance_json)}',
            '{_escape_sql_string(delivery_json)}',
            '{_escape_sql_string(meta_json)}',
            {_format_datetime(now)},
            {_format_datetime(now)},
            {last_saved_draft_at_value},
            {applied_at_value}
        )
        """
        await execute_ch_query(insert_query)
    else:
        insert_query = f"""
        INSERT INTO {TABLE_NAME} (
            rule_code, rule_name, enabled, status, mode,
            basic_config, ast_config, governance, delivery, meta,
            created_at, updated_at
        ) VALUES (
            '{_escape_sql_string(rule_code)}',
            {_serialize_json_field(payload.rule_name)},
            {payload.enabled.value if hasattr(payload.enabled, 'value') else payload.enabled},
            '{payload.status.value if hasattr(payload.status, 'value') else payload.status}',
            '{payload.mode.value if hasattr(payload.mode, 'value') else payload.mode}',
            '{_escape_sql_string(basic_config_json)}',
            '{_escape_sql_string(ast_config_json)}',
            '{_escape_sql_string(governance_json)}',
            '{_escape_sql_string(delivery_json)}',
            '{_escape_sql_string(meta_json)}',
            {_format_datetime(now)},
            {_format_datetime(now)}
        )
        """
        await execute_ch_query(insert_query)

        new_snapshot_dict = {
            "rule_code": rule_code,
            "rule_name": payload.rule_name,
            "enabled": payload.enabled.value if hasattr(payload.enabled, 'value') else payload.enabled,
            "status": payload.status.value if hasattr(payload.status, 'value') else payload.status,
            "mode": payload.mode.value if hasattr(payload.mode, 'value') else payload.mode,
            "basic_config": payload.basic_config or {},
            "ast_config": payload.ast_config or {},
            "governance": payload.governance or {},
            "delivery": payload.delivery or {},
            "meta": payload.meta or {},
        }
        new_snapshot_json = json.dumps(new_snapshot_dict, ensure_ascii=False)
        history_insert_query = f"""
        INSERT INTO {HISTORY_TABLE_NAME} (
            rule_code, action, operator, snapshot_data, created_at
        ) VALUES (
            '{_escape_sql_string(rule_code)}',
            '{action}',
            'system',
            '{_escape_sql_string(new_snapshot_json)}',
            {_format_datetime(now)}
        )
        """
        await execute_ch_query(history_insert_query)

    response_data = {
        "rule_code": rule_code,
        "rule_name": payload.rule_name,
        "enabled": payload.enabled.value if hasattr(payload.enabled, 'value') else payload.enabled,
        "status": payload.status.value if hasattr(payload.status, 'value') else payload.status,
        "mode": payload.mode.value if hasattr(payload.mode, 'value') else payload.mode,
        "basic_config": payload.basic_config or {},
        "ast_config": payload.ast_config or {},
        "governance": payload.governance or {},
        "delivery": payload.delivery or {},
        "meta": payload.meta or {},
        "created_at": now,
        "updated_at": now,
    }
    return Result.success(data=SubscriptionTopicResponse(**response_data))


@router.get("/{rule_code}/history", response_model=Result[List[HistoryRecordItem]])
async def get_rule_history(rule_code: str = PathParam(..., description="规则CODE")):
    query = f"""
    SELECT history_id, rule_code, action, operator, snapshot_data, created_at
    FROM {HISTORY_TABLE_NAME}
    WHERE rule_code = '{_escape_sql_string(rule_code)}'
    ORDER BY created_at DESC
    """

    result = await execute_ch_query(query)
    data = result.get("data", [])

    items = []
    for row in data:
        snapshot_str = row.get("snapshot_data", "{}")
        try:
            snapshot_data = json.loads(snapshot_str) if snapshot_str else {}
        except json.JSONDecodeError:
            snapshot_data = {}

        item = HistoryRecordItem(
            history_id=row.get("history_id", ""),
            rule_code=row.get("rule_code", ""),
            action=row.get("action", ""),
            operator=row.get("operator", ""),
            snapshot_data=snapshot_data,
            created_at=row.get("created_at"),
        )
        items.append(item)

    return Result.success(data=items)


@router.post("/{rule_code}/rollback/{history_id}", response_model=Result[SubscriptionTopicResponse])
async def rollback_rule(
    rule_code: str = PathParam(..., description="规则CODE"),
    history_id: str = PathParam(..., description="历史记录ID"),
):
    query = f"""
    SELECT snapshot_data, created_at
    FROM {HISTORY_TABLE_NAME}
    WHERE history_id = '{_escape_sql_string(history_id)}' AND rule_code = '{_escape_sql_string(rule_code)}'
    """

    result = await execute_ch_query(query)
    data = result.get("data", [])

    if not data:
        raise HTTPException(status_code=404, detail=f"历史记录 {history_id} 不存在")

    snapshot_str = data[0].get("snapshot_data", "{}")
    try:
        snapshot_data = json.loads(snapshot_str) if snapshot_str else {}
    except json.JSONDecodeError:
        snapshot_data = {}

    now = datetime.now()
    rule_code_to_use = snapshot_data.get("id") or rule_code
    snapshot_data["id"] = rule_code_to_use

    basic_config_json = json.dumps(snapshot_data.get("basic_config", {}), ensure_ascii=False)
    ast_config_json = json.dumps(snapshot_data.get("ast_config", {}), ensure_ascii=False)
    governance_json = json.dumps(snapshot_data.get("governance", {}), ensure_ascii=False)
    delivery_json = json.dumps(snapshot_data.get("delivery", {}), ensure_ascii=False)
    meta_json = json.dumps(snapshot_data.get("meta", {}), ensure_ascii=False)

    delete_query = f"""
    ALTER TABLE {TABLE_NAME} DELETE WHERE rule_code = '{_escape_sql_string(rule_code_to_use)}'
    """
    await execute_ch_query(delete_query)

    insert_query = f"""
    INSERT INTO {TABLE_NAME} (
        rule_code, rule_name, enabled, status, mode,
        basic_config, ast_config, governance, delivery, meta,
        created_at, updated_at
    ) VALUES (
        '{_escape_sql_string(rule_code_to_use)}',
        {_serialize_json_field(snapshot_data.get("rule_name"))},
        {snapshot_data.get("enabled", 1)},
        '{snapshot_data.get("status", "draft")}',
        '{snapshot_data.get("mode", "basic")}',
        '{_escape_sql_string(basic_config_json)}',
        '{_escape_sql_string(ast_config_json)}',
        '{_escape_sql_string(governance_json)}',
        '{_escape_sql_string(delivery_json)}',
        '{_escape_sql_string(meta_json)}',
        {_format_datetime(now)},
        {_format_datetime(now)}
    )
    """
    await execute_ch_query(insert_query)

    rollback_snapshot = json.dumps(snapshot_data, ensure_ascii=False)
    history_insert_query = f"""
    INSERT INTO {HISTORY_TABLE_NAME} (
        rule_code, action, operator, snapshot_data, created_at
    ) VALUES (
        '{_escape_sql_string(rule_code_to_use)}',
        'rollback',
        'system',
        '{_escape_sql_string(rollback_snapshot)}',
        {_format_datetime(now)}
    )
    """
    await execute_ch_query(history_insert_query)

    response_data = {
        "rule_code": rule_code_to_use,
        "rule_name": snapshot_data.get("rule_name"),
        "enabled": snapshot_data.get("enabled", 1),
        "status": snapshot_data.get("status", "draft"),
        "mode": snapshot_data.get("mode", "basic"),
        "basic_config": snapshot_data.get("basic_config", {}),
        "ast_config": snapshot_data.get("ast_config", {}),
        "governance": snapshot_data.get("governance", {}),
        "delivery": snapshot_data.get("delivery", {}),
        "meta": snapshot_data.get("meta", {}),
        "created_at": now,
        "updated_at": now,
    }
    return Result.success(data=SubscriptionTopicResponse(**response_data))
