import json
from datetime import datetime
from typing import Any, List

from fastapi import APIRouter, HTTPException, Path as PathParam

from app.schemas.topic import SubscriptionTopicCreate, SubscriptionTopicResponse, SubscriptionTopicListItem, TopicIdNameItem
from app.schemas.base import Result
from app.utils.ch_client import execute_ch_query
from app.config.config import ch_settings

router = APIRouter(prefix="/api/topics", tags=["专题管理"])

DATABASE = ch_settings.DATABASE
TABLE_NAME = f"{DATABASE}.subscription_topics"
ALERT_TABLE_NAME = "hawkeye_test.hawkeye_ads_alert_event_latest"
ALERT_STATUS_TABLE_NAME = "hawkeye_test.hawkeye_dwd_alert_event_status"


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
        "last_saved_draft_at": now,
        "applied_at": now,
        "deleted_at": None,
        "final_syn_time": None,
    }

    return Result.success(data=SubscriptionTopicResponse(**response_data))


@router.get("/list", response_model=Result[list[SubscriptionTopicListItem]])
async def list_topics():
    query = f"""
    SELECT rule_code, rule_name, enabled, meta, final_syn_time
    FROM {TABLE_NAME}
    WHERE deleted_at IS NULL
    ORDER BY created_at DESC
    """

    result = await execute_ch_query(query)
    data = result.get("data", [])

    items = []
    for row in data:
        meta_str = row.get("meta", "")
        meta_dict = {}
        if meta_str:
            try:
                meta_dict = json.loads(meta_str)
            except json.JSONDecodeError:
                meta_dict = {}

        item = SubscriptionTopicListItem(
            rule_code=row.get("rule_code", ""),
            rule_name=row.get("rule_name"),
            enabled=row.get("enabled"),
            charge_person=meta_dict.get("charge_person"),
            summary=meta_dict.get("summary"),
            final_syn_time=row.get("final_syn_time"),
        )
        items.append(item)

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
    data = result.get("data", [])

    items = []
    for row in data:
        item = TopicIdNameItem(
            rule_code=row.get("rule_code", ""),
            rule_name=row.get("rule_name"),
        )
        items.append(item)

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
async def toggle_topic(rule_code: str = PathParam(..., description="专题CODE")):
    print(f"\n{'='*60}")
    print(f"[TOGGLE TOPIC] Toggling rule_code={rule_code}")
    print(f"{'='*60}")

    query = f"""
    SELECT rule_code, enabled
    FROM {TABLE_NAME}
    WHERE rule_code = '{_escape_sql_string(rule_code)}' AND deleted_at IS NULL
    """

    result = await execute_ch_query(query)
    data = result.get("data", [])

    if not data:
        raise HTTPException(status_code=404, detail=f"专题 {rule_code} 不存在")

    current_enabled = data[0].get("enabled", 1)
    new_enabled = 0 if current_enabled == 1 else 1
    action = "停用" if new_enabled == 0 else "启动"

    alter_query = f"""
    ALTER TABLE {TABLE_NAME}
    UPDATE enabled = {new_enabled}
    WHERE rule_code = '{_escape_sql_string(rule_code)}'
    """

    try:
        await execute_ch_query(alter_query)
    except Exception as e:
        pass

    print(f"[TOGGLE TOPIC] Topic {rule_code} has been {'disabled' if new_enabled == 0 else 'enabled'}")
    print(f"{'='*60}\n")

    return Result.success(data={
        "rule_code": rule_code,
        "enabled": new_enabled,
        "message": f"专题已{action}"
    })


from app.schemas.alert import AlertListItem, AlertDetailResponse, RuleNameStatItem
from app.crud.alert import get_alert_list_all, get_alert_detail, get_rule_name_stats, get_alert_list_by_threat_category, get_alert_list_by_topic_name
from app.crud.alert import _execute_ch_query


@router.get("/alert/list_all", response_model=Result[List[AlertListItem]])
def list_alert_all():
    """
    获取告警信息列表的全部数据
    """
    result = get_alert_list_all()
    return Result.success(data=result["items"], msg=f"共 {result['total']} 条")


@router.get("/alert/list", response_model=Result[List[AlertListItem]])
def list_alert_by_threat_category(threat_category: str):
    """
    根据threat_category过滤告警数据
    """
    result = get_alert_list_by_threat_category(threat_category)
    return Result.success(data=result["items"], msg=f"共 {result['total']} 条")


@router.get("/alert/list_by_topic_name", response_model=Result[List[AlertListItem]])
def list_alert_by_topic_name(name: str):
    """
    根据订阅名称(rule_name)获取告警列表
    - name: 订阅名称，匹配hawkeye_ads_alert_event_latest表的threat_category字段
    """
    result = get_alert_list_by_topic_name(name)
    return Result.success(data=result["items"], msg=f"共 {result['total']} 条")


@router.get("/alert/rule_name_stats", response_model=Result[List[RuleNameStatItem]])
def get_rule_name_statistics():
    """
    获取rule_name出现次数前5名统计
    """
    result = get_rule_name_stats()
    return Result.success(data=result, msg=f"共 {len(result)} 条")


@router.post("/alert/{event_id}/toggle_read", response_model=Result[dict])
def toggle_alert_read(event_id: str):
    """
    切换告警已读/未读状态
    - event_id: 告警事件ID
    - 同时更新 hawkeye_ads_alert_event_latest 和 hawkeye_dwd_alert_event_status 两张表
    - 返回新的已读状态
    """
    check_query = f"""
    SELECT event_id FROM {ALERT_TABLE_NAME}
    WHERE event_id = '{_escape_sql_string(event_id)}'
    """
    result = _execute_ch_query(check_query)
    data = result.get("data", [])
    if not data:
        raise HTTPException(status_code=404, detail=f"告警事件 {event_id} 不存在")

    read_status = data[0].get("read_status", 0)
    new_read_status = 0 if read_status == 1 else 1

    alter_query_1 = f"""
    ALTER TABLE {ALERT_TABLE_NAME}
    UPDATE read_status = {new_read_status}
    WHERE event_id = '{_escape_sql_string(event_id)}'
    """
    alter_query_2 = f"""
    ALTER TABLE {ALERT_STATUS_TABLE_NAME}
    UPDATE read_status = {new_read_status}
    WHERE event_id = '{_escape_sql_string(event_id)}'
    """
    try:
        _execute_ch_query(alter_query_1)
        _execute_ch_query(alter_query_2)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新已读状态失败: {str(e)}")

    return Result.success(data={
        "event_id": event_id,
        "read_status": new_read_status
    }, msg="已读状态已更新")


@router.post("/alert/{event_id}/monitor", response_model=Result[dict])
def toggle_alert_monitor(event_id: str):
    """
    关注/取消关注告警
    - event_id: 告警事件ID
    - 切换 is_monitor_target 字段（0/1）
    - 同时更新 hawkeye_ads_alert_event_latest 和 hawkeye_dwd_alert_event_status 两张表
    """
    check_query = f"""
    SELECT event_id, is_monitor_target FROM {ALERT_TABLE_NAME}
    WHERE event_id = '{_escape_sql_string(event_id)}'
    """
    result = _execute_ch_query(check_query)
    data = result.get("data", [])
    if not data:
        raise HTTPException(status_code=404, detail=f"告警事件 {event_id} 不存在")

    current_status = data[0].get("is_monitor_target", 0)
    new_status = 0 if current_status == 1 else 1

    alter_query_1 = f"""
    ALTER TABLE {ALERT_TABLE_NAME}
    UPDATE is_monitor_target = {new_status}
    WHERE event_id = '{_escape_sql_string(event_id)}'
    """
    alter_query_2 = f"""
    ALTER TABLE {ALERT_STATUS_TABLE_NAME}
    UPDATE is_monitor_target = {new_status}
    WHERE event_id = '{_escape_sql_string(event_id)}'
    """
    try:
        _execute_ch_query(alter_query_1)
        _execute_ch_query(alter_query_2)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新关注状态失败: {str(e)}")

    return Result.success(data={
        "event_id": event_id,
        "is_monitor_target": new_status
    }, msg="关注状态已更新")


@router.get("/alert/{event_id}/detail", response_model=Result[AlertDetailResponse])
def get_alert_detail_route(event_id: str, content_id: str):
    """
    获取告警详情
    - event_id: 告警事件ID
    - content_id: 内容ID（用于查询原文正文）
    - 返回 title、author_name、raw_content
    """
    result = get_alert_detail(event_id, content_id)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result["message"])
    return Result.success(data=AlertDetailResponse(
        title=result["title"],
        author_name=result["author_name"],
        raw_content=result["raw_content"]
    ))


@router.post("/alert/{event_id}/export", response_model=Result[dict])
def export_alert(event_id: str):
    """
    导出告警，将export_status字段设置为1
    - event_id: 告警事件ID
    - 同时更新 hawkeye_ads_alert_event_latest 和 hawkeye_dwd_alert_event_status 两张表
    """
    check_query = f"""
    SELECT event_id FROM {ALERT_TABLE_NAME}
    WHERE event_id = '{_escape_sql_string(event_id)}'
    """
    result = _execute_ch_query(check_query)
    data = result.get("data", [])
    if not data:
        raise HTTPException(status_code=404, detail=f"告警事件 {event_id} 不存在")

    alter_query_1 = f"""
    ALTER TABLE {ALERT_TABLE_NAME}
    UPDATE export_status = 1
    WHERE event_id = '{_escape_sql_string(event_id)}'
    """
    alter_query_2 = f"""
    ALTER TABLE {ALERT_STATUS_TABLE_NAME}
    UPDATE export_status = 1
    WHERE event_id = '{_escape_sql_string(event_id)}'
    """
    try:
        _execute_ch_query(alter_query_1)
        _execute_ch_query(alter_query_2)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新导出状态失败: {str(e)}")

    return Result.success(data={
        "event_id": event_id,
        "export_status": 1
    }, msg="导出状态已更新")


@router.post("/alert/{event_id}/false_positive", response_model=Result[dict])
def mark_false_positive(event_id: str):
    """
    标记误报，将false_positive字段设置为1
    - event_id: 告警事件ID
    - 同时更新 hawkeye_ads_alert_event_latest 和 hawkeye_dwd_alert_event_status 两张表
    """
    check_query = f"""
    SELECT event_id FROM {ALERT_TABLE_NAME}
    WHERE event_id = '{_escape_sql_string(event_id)}'
    """
    result = _execute_ch_query(check_query)
    data = result.get("data", [])
    if not data:
        raise HTTPException(status_code=404, detail=f"告警事件 {event_id} 不存在")

    alter_query_1 = f"""
    ALTER TABLE {ALERT_TABLE_NAME}
    UPDATE false_positive = 1
    WHERE event_id = '{_escape_sql_string(event_id)}'
    """
    alter_query_2 = f"""
    ALTER TABLE {ALERT_STATUS_TABLE_NAME}
    UPDATE false_positive = 1
    WHERE event_id = '{_escape_sql_string(event_id)}'
    """
    try:
        _execute_ch_query(alter_query_1)
        _execute_ch_query(alter_query_2)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"标记误报失败: {str(e)}")

    return Result.success(data={
        "event_id": event_id,
        "false_positive": 1
    }, msg="已标记为误报")