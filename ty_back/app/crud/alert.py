from typing import List, Dict, Any
import httpx
from app.config.config import ch_settings


def _execute_ch_query(query: str) -> Dict[str, Any]:
    url = f"http://{ch_settings.HOST}:{ch_settings.PORT}/"
    params = {
        "query": query,
        "user": ch_settings.USER,
        "password": ch_settings.PASSWORD,
        "database": ch_settings.DATABASE,
    }
    is_write_query = any(q.strip().upper().startswith(("ALTER", "INSERT", "UPDATE", "DELETE")) for q in query.split(";"))
    if not is_write_query:
        params["default_format"] = "JSON"

    with httpx.Client(timeout=30.0) as client:
        if is_write_query:
            write_params = {
                "query": query,
                "user": ch_settings.USER,
                "password": ch_settings.PASSWORD,
                "database": ch_settings.DATABASE,
            }
            response = client.post(url, params=write_params)
            if response.status_code != 200:
                response.raise_for_status()
            return {"success": True}
        response = client.post(url, params=params)
        response.raise_for_status()
        try:
            return response.json()
        except Exception:
            return {"data": [], "statistics": {}}


def get_alert_list_all() -> Dict[str, Any]:
    query = """
        SELECT
            event_id,
            rule_code,
            rule_name,
            title,
            text_preview,
            author_name,
            platform,
            site_name,
            report_time,
            severity,
            region,
            topic,
            industry,
            read_status,
            entity_tags,
            content_id,
            false_positive,
            export_status,
            search_title_text,
            media_name,
            threat_category,
            source_type,
            channel_id,
            source_handle,
            entity_values_text
        FROM hawkeye_test.hawkeye_ads_alert_event_latest
        WHERE false_positive != 1
        ORDER BY report_time DESC
    """

    result = _execute_ch_query(query)
    rows = result.get("data", [])
    total = len(rows)

    items = []
    for row in rows:
        item = {
            "event_id": row.get("event_id"),
            "rule_code": row.get("rule_code"),
            "rule_name": row.get("rule_name"),
            "title": row.get("title"),
            "text_preview": row.get("text_preview"),
            "author_name": row.get("author_name"),
            "platform": row.get("platform"),
            "site_name": row.get("site_name"),
            "report_time": row.get("report_time"),
            "severity": row.get("severity"),
            "region": row.get("region"),
            "topic": row.get("topic"),
            "industry": row.get("industry"),
            "read_status": row.get("read_status"),
            "entity_tags": row.get("entity_tags", []),
            "content_id": row.get("content_id"),
            "false_positive": row.get("false_positive"),
            "export_status": row.get("export_status"),
            "search_title_text": row.get("search_title_text"),
            "media_name": row.get("media_name"),
            "threat_category": row.get("threat_category"),
            "source_type": row.get("source_type"),
            "channel_id": row.get("channel_id"),
            "source_handle": row.get("source_handle"),
            "entity_values_text": row.get("entity_values_text"),
        }
        items.append(item)

    return {"total": total, "items": items}


def get_rule_name_stats() -> List[Dict[str, Any]]:
    query = """
        SELECT rule_name, count() as count
        FROM hawkeye_test.hawkeye_ads_alert_event_latest
        GROUP BY rule_name
        ORDER BY count DESC
        LIMIT 5
    """

    result = _execute_ch_query(query)
    rows = result.get("data", [])

    items = []
    for row in rows:
        item = {
            "rule_name": row.get("rule_name"),
            "count": row.get("count"),
        }
        items.append(item)

    return items


def get_alert_list_by_threat_category(threat_category: str) -> Dict[str, Any]:
    query = f"""
        SELECT
            event_id,
            rule_code,
            rule_name,
            title,
            text_preview,
            author_name,
            platform,
            site_name,
            report_time,
            severity,
            region,
            topic,
            industry,
            read_status,
            entity_tags,
            content_id,
            false_positive,
            export_status,
            search_title_text,
            media_name,
            threat_category,
            source_type,
            channel_id,
            source_handle,
            entity_values_text
        FROM hawkeye_test.hawkeye_ads_alert_event_latest
        WHERE threat_category = '{threat_category}'
        ORDER BY report_time DESC
    """

    result = _execute_ch_query(query)
    rows = result.get("data", [])
    total = len(rows)

    items = []
    for row in rows:
        item = {
            "event_id": row.get("event_id"),
            "rule_code": row.get("rule_code"),
            "rule_name": row.get("rule_name"),
            "title": row.get("title"),
            "text_preview": row.get("text_preview"),
            "author_name": row.get("author_name"),
            "platform": row.get("platform"),
            "site_name": row.get("site_name"),
            "report_time": row.get("report_time"),
            "severity": row.get("severity"),
            "region": row.get("region"),
            "topic": row.get("topic"),
            "industry": row.get("industry"),
            "read_status": row.get("read_status"),
            "entity_tags": row.get("entity_tags", []),
            "content_id": row.get("content_id"),
            "false_positive": row.get("false_positive"),
            "export_status": row.get("export_status"),
            "search_title_text": row.get("search_title_text"),
            "media_name": row.get("media_name"),
            "threat_category": row.get("threat_category"),
            "source_type": row.get("source_type"),
            "channel_id": row.get("channel_id"),
            "source_handle": row.get("source_handle"),
            "entity_values_text": row.get("entity_values_text"),
        }
        items.append(item)

    return {"total": total, "items": items}


def get_alert_list_by_topic_name(threat_category: str) -> Dict[str, Any]:
    query = f"""
        SELECT
            event_id,
            rule_code,
            rule_name,
            title,
            text_preview,
            author_name,
            platform,
            site_name,
            report_time,
            severity,
            region,
            topic,
            industry,
            read_status,
            entity_tags,
            content_id,
            false_positive,
            export_status,
            search_title_text,
            media_name,
            threat_category,
            source_type,
            channel_id,
            source_handle,
            entity_values_text
        FROM hawkeye_test.hawkeye_ads_alert_event_latest
        WHERE threat_category = '{threat_category}'
        ORDER BY report_time DESC
    """

    result = _execute_ch_query(query)
    rows = result.get("data", [])
    total = len(rows)

    items = []
    for row in rows:
        item = {
            "event_id": row.get("event_id"),
            "rule_code": row.get("rule_code"),
            "rule_name": row.get("rule_name"),
            "title": row.get("title"),
            "text_preview": row.get("text_preview"),
            "author_name": row.get("author_name"),
            "platform": row.get("platform"),
            "site_name": row.get("site_name"),
            "report_time": row.get("report_time"),
            "severity": row.get("severity"),
            "region": row.get("region"),
            "topic": row.get("topic"),
            "industry": row.get("industry"),
            "read_status": row.get("read_status"),
            "entity_tags": row.get("entity_tags", []),
            "content_id": row.get("content_id"),
            "false_positive": row.get("false_positive"),
            "export_status": row.get("export_status"),
            "search_title_text": row.get("search_title_text"),
            "media_name": row.get("media_name"),
            "threat_category": row.get("threat_category"),
            "source_type": row.get("source_type"),
            "channel_id": row.get("channel_id"),
            "source_handle": row.get("source_handle"),
            "entity_values_text": row.get("entity_values_text"),
        }
        items.append(item)

    return {"total": total, "items": items}


def toggle_alert_read_status(event_id: str) -> Dict[str, Any]:
    current_status_query = f"""
        SELECT read_status
        FROM hawkeye_test.hawkeye_ads_alert_event_latest
        WHERE event_id = '{event_id}'
    """
    result = _execute_ch_query(current_status_query)
    rows = result.get("data", [])
    if not rows:
        return {"success": False, "message": "告警不存在"}

    current_status = rows[0].get("read_status", 0)
    new_status = 0 if current_status == 1 else 1

    update_query = f"""
        ALTER TABLE hawkeye_test.hawkeye_ads_alert_event_latest
        UPDATE read_status = {new_status}
        WHERE event_id = '{event_id}'
    """
    _execute_ch_query(update_query)

    return {"success": True, "event_id": event_id, "read_status": new_status}


def toggle_alert_false_positive(event_id: str) -> Dict[str, Any]:
    current_status_query = f"""
        SELECT false_positive
        FROM hawkeye_test.hawkeye_ads_alert_event_latest
        WHERE event_id = '{event_id}'
    """
    result = _execute_ch_query(current_status_query)
    rows = result.get("data", [])
    if not rows:
        return {"success": False, "message": "告警不存在"}

    current_status = rows[0].get("false_positive", 0)
    new_status = 0 if current_status == 1 else 1

    update_query = f"""
        ALTER TABLE hawkeye_test.hawkeye_ads_alert_event_latest
        UPDATE false_positive = {new_status}
        WHERE event_id = '{event_id}'
    """
    _execute_ch_query(update_query)

    return {"success": True, "event_id": event_id, "false_positive": new_status}


def get_alert_detail(event_id: str, content_id: str) -> Dict[str, Any]:
    alert_query = f"""
        SELECT title, author_name
        FROM hawkeye_test.hawkeye_ads_alert_event_latest
        WHERE event_id = '{event_id}'
    """
    alert_result = _execute_ch_query(alert_query)
    alert_rows = alert_result.get("data", [])
    if not alert_rows:
        return {"success": False, "message": "告警不存在"}

    title = alert_rows[0].get("title")
    author_name = alert_rows[0].get("author_name")

    content_query = f"""
        SELECT raw_content
        FROM hawkeye_test.hawkeye_dwd_intel_content_cold
        WHERE content_id = '{content_id}'
    """
    content_result = _execute_ch_query(content_query)
    content_rows = content_result.get("data", [])
    raw_content = content_rows[0].get("raw_content") if content_rows else None

    return {
        "success": True,
        "title": title,
        "author_name": author_name,
        "raw_content": raw_content
    }