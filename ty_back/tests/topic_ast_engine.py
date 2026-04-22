from __future__ import annotations

import argparse
import json
import re
import time
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


APP = {
    "schema": "router_gw_v14.0",
    "adapter": "1.2",
    "regex_max_len": 200,
}

SEVERITY_ORDER: Dict[str, int] = {
    "ALL": 0,
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "CRITICAL": 4,
}

SCHEMA_TOPICS = [
    {"id": "TopicDrugs", "name": "毒品交易"},
    {"id": "TopicSmuggle", "name": "非法走私"},
    {"id": "TopicTerror", "name": "恐怖暴力"},
    {"id": "TopicDataLeak", "name": "数据泄露"},
    {"id": "TopicCybercrime", "name": "网络黑产"},
    {"id": "TopicAPT", "name": "APT攻击"},
]
TOPIC_NAME_MAP = {item["id"]: item["name"] for item in SCHEMA_TOPICS}

FIELDS = [
    {"v": "threat_category", "type": "string"},
    {"v": "severity", "type": "string"},
    {"v": "risk_score", "type": "number"},
    {"v": "confidence_score", "type": "number"},
    {"v": "source_platform", "type": "string"},
    {"v": "source_handle", "type": "string"},
    {"v": "discovery_source", "type": "string"},
    {"v": "query_family", "type": "string"},
    {"v": "labels", "type": "array"},
    {"v": "matched_terms", "type": "array"},
    {"v": "ioc_location", "type": "array"},
    {"v": "ioc_crypto", "type": "array"},
    {"v": "ioc_url", "type": "array"},
    {"v": "ioc_phone", "type": "array"},
    {"v": "ioc_email", "type": "array"},
    {"v": "entity_type", "type": "string"},
    {"v": "entity_value", "type": "string"},
    {"v": "entity_types", "type": "array"},
    {"v": "entity_values", "type": "array"},
    {"v": "suppressed", "type": "boolean"},
    {"v": "content_hash", "type": "string"},
    {"v": "raw_content", "type": "string"},
]
FIELD_TYPE_MAP = {item["v"]: item["type"] for item in FIELDS}


def safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def uniq(seq: List[Any]) -> List[Any]:
    out: List[Any] = []
    seen = set()
    for item in seq:
        key = json.dumps(item, ensure_ascii=False, sort_keys=True) if isinstance(item, (dict, list)) else item
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def csv_to_list(text: Any) -> List[str]:
    return [part.strip() for part in str(text or "").split(",") if part.strip()]


def now_ms() -> int:
    return int(time.time() * 1000)


def new_trace_id() -> str:
    return f"tr_{int(time.time() * 1000000):x}"


def canon(field: str, value: Any) -> Any:
    if value is None:
        return None
    if field == "source_handle":
        v = str(value).strip()
        if v and not v.startswith("@") and not v.startswith("-100"):
            v = "@" + v
        return v.lower()
    if field == "severity":
        return str(value).strip().upper()
    if field == "content_hash":
        return str(value).strip().lower()
    if isinstance(value, str):
        return value.strip()
    return value


def stable_hash(text: str) -> str:
    # 对齐 config.html 中的 Math.imul(31, hash) + charCode 的 32 位有符号行为
    h = 0
    for ch in text:
        h = ((h * 31) + ord(ch)) & 0xFFFFFFFF
    if h >= 0x80000000:
        h -= 0x100000000
    return str(h)


def _to_number(value: Any) -> Optional[float]:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _normalize_string_list(values: Any, field: str) -> List[str]:
    if not isinstance(values, list):
        return []
    out: List[str] = []
    for item in values:
        if isinstance(item, str):
            out.append(canon(field, item))
        elif isinstance(item, dict):
            for key in ("label", "name", "tag", "value"):
                if key in item and item[key]:
                    out.append(canon(field, item[key]))
                    break
    return uniq(out)


def normalize_engine_output(raw: Dict[str, Any]) -> Dict[str, Any]:
    r = raw or {}
    out: Dict[str, Any] = {}

    out["threat_category"] = r.get("threat_category") or r.get("topic") or r.get("category") or ""
    out["severity"] = canon("severity", r.get("severity") or "")
    out["risk_score"] = _to_number(r.get("risk_score"))
    out["confidence_score"] = _to_number(r.get("confidence_score"))
    out["source_platform"] = r.get("source_platform") or r.get("platform") or ""
    out["source_handle"] = canon("source_handle", r.get("source_handle") or r.get("source") or r.get("channel") or "")
    out["discovery_source"] = r.get("discovery_source") or r.get("discovery") or ""
    out["query_family"] = r.get("query_family") or r.get("pipeline") or r.get("model_family") or ""
    out["raw_content"] = r.get("raw_content") or r.get("content") or r.get("text") or ""

    suppressed = r.get("suppressed")
    if isinstance(suppressed, bool):
        out["suppressed"] = suppressed
    elif suppressed in ("true", "false"):
        out["suppressed"] = suppressed == "true"
    else:
        out["suppressed"] = None

    out["labels"] = _normalize_string_list(r.get("labels"), "labels")

    matched_terms: List[str] = []
    if isinstance(r.get("matched_terms"), list):
        matched_terms = [str(x) for x in r["matched_terms"] if isinstance(x, str)]
    elif isinstance(r.get("matched_terms"), dict):
        for arr in r["matched_terms"].values():
            if isinstance(arr, list):
                matched_terms.extend(str(x) for x in arr if isinstance(x, str))
    out["matched_terms"] = uniq(matched_terms)

    entities = safe_list(r.get("entities"))
    entity_types: List[str] = []
    entity_values: List[str] = []
    for entity in entities:
        if not isinstance(entity, dict):
            continue
        if entity.get("type"):
            entity_types.append(canon("entity_type", str(entity["type"])))
        if entity.get("value"):
            entity_values.append(canon("entity_value", str(entity["value"])))

    out["entity_types"] = uniq(entity_types)
    out["entity_values"] = uniq(entity_values)
    out["entity_type"] = canon("entity_type", r.get("entity_type") or (out["entity_types"][0] if out["entity_types"] else ""))
    out["entity_value"] = canon("entity_value", r.get("entity_value") or (out["entity_values"][0] if out["entity_values"] else ""))

    extracted_iocs = r.get("extracted_iocs") if isinstance(r.get("extracted_iocs"), dict) else {}

    def ioc_get(key: str) -> List[str]:
        value = extracted_iocs.get(key)
        if value is None and key in r:
            value = r.get(key)
        if isinstance(value, list):
            return uniq([canon(f"ioc_{key}", item) for item in value if item not in (None, "")])
        if isinstance(value, str):
            return [canon(f"ioc_{key}", value)] if value.strip() else []
        return []

    out["ioc_location"] = ioc_get("location") or safe_list(r.get("ioc_location"))
    out["ioc_crypto"] = ioc_get("crypto") or safe_list(r.get("ioc_crypto"))
    out["ioc_url"] = ioc_get("url") or safe_list(r.get("ioc_url"))
    out["ioc_phone"] = ioc_get("phone") or safe_list(r.get("ioc_phone"))
    out["ioc_email"] = ioc_get("email") or safe_list(r.get("ioc_email"))

    # 对齐前端：优先 raw_content，否则取原始对象前 2000 字符参与 hash
    out["content_hash"] = stable_hash(out["raw_content"] or json.dumps(r, ensure_ascii=False, sort_keys=True)[:2000])

    timestamp = r.get("timestamp", r.get("event_time", r.get("time")))
    if isinstance(timestamp, (int, float)):
        out["event_time"] = int(timestamp)
    elif isinstance(timestamp, str):
        try:
            # 兼容 ISO8601
            out["event_time"] = int(__import__("datetime").datetime.fromisoformat(timestamp.replace("Z", "+00:00")).timestamp() * 1000)
        except ValueError:
            out["event_time"] = now_ms()
    else:
        out["event_time"] = now_ms()

    # 清理 fallback 顶层 IOC 为 config.html 风格的 canon 值
    for field in ("ioc_location", "ioc_crypto", "ioc_url", "ioc_phone", "ioc_email"):
        out[field] = uniq([canon(field, item) for item in safe_list(out[field]) if item not in (None, "")])

    return out


def walk_ast(node: Optional[Dict[str, Any]], cb) -> None:
    if not isinstance(node, dict):
        return
    cb(node)
    for child in safe_list(node.get("children")):
        walk_ast(child, cb)


def count_ast_conditions(node: Optional[Dict[str, Any]]) -> int:
    if not isinstance(node, dict):
        return 0
    if node.get("type") == "COND":
        return 1
    return sum(count_ast_conditions(child) for child in safe_list(node.get("children")))


def has_empty_ast_root(rule: Dict[str, Any]) -> bool:
    return rule.get("mode") == "ast" and (not isinstance(rule.get("ast"), dict) or not safe_list(rule["ast"].get("children")))


def validate_rule(rule: Dict[str, Any]) -> Dict[str, List[str]]:
    errors: List[str] = []
    warnings: List[str] = []

    if not str(rule.get("name") or "").strip():
        errors.append("规则名称不能为空")

    if rule.get("mode") == "ast":
        if has_empty_ast_root(rule):
            errors.append("AST 专家模式下，根条件组为空")
        else:
            def _check(node: Dict[str, Any]) -> None:
                if node.get("type") == "COND" and node.get("op") == "regex":
                    pattern = str(node.get("value") or "")
                    try:
                        re.compile(pattern)
                    except re.error as exc:
                        errors.append(f"无效的正则表达式语法: {pattern} ({exc})")
                    if len(pattern) > 100:
                        warnings.append("正则表达式过于复杂(>100字符)，可能存在 ReDoS 性能隐患")
            walk_ast(rule.get("ast"), _check)

    priority = rule.get("meta", {}).get("priority", 50)
    try:
        priority_int = int(priority)
        if not 1 <= priority_int <= 100:
            errors.append("规则优先级必须是 1 到 100 之间的数值")
    except (TypeError, ValueError):
        errors.append("规则优先级必须是 1 到 100 之间的数值")

    return {"errors": errors, "warnings": warnings}


def _default_basic() -> Dict[str, Any]:
    return {
        "topics": [],
        "severity": "MEDIUM",
        "risk_min": None,
        "locations": [],
        "labels": [],
    }


def _default_ast() -> Dict[str, Any]:
    return {"type": "GROUP", "op": "AND", "children": []}


def normalize_rule(rule: Dict[str, Any]) -> Dict[str, Any]:
    r = deepcopy(rule)

    mode = r.get("mode")
    basic = deepcopy(r.get("basic") or _default_basic())
    ast = deepcopy(r.get("ast") or _default_ast())

    if isinstance(r.get("match"), dict):
        match = r["match"]
        match_type = str(match.get("type") or "").upper()
        if match_type == "AST":
            mode = "ast"
            ast = deepcopy(match.get("ast") or _default_ast())
        elif match_type == "BASIC":
            mode = "basic"
            basic = {
                "topics": safe_list(match.get("topics")),
                "severity": match.get("severity") or "MEDIUM",
                "risk_min": match.get("risk_min"),
                "locations": safe_list(match.get("locations")),
                "labels": safe_list(match.get("labels")),
            }

    if mode not in ("basic", "ast"):
        mode = "ast" if isinstance(ast, dict) and ast else "basic"

    normalized = {
        "id": r.get("id") or f"rule_{int(time.time() * 1000)}",
        "name": r.get("name") or "未命名规则",
        "enabled": bool(r.get("enabled", True)),
        "status": r.get("status", "draft"),
        "mode": mode,
        "basic": {
            "topics": uniq([str(x).strip() for x in safe_list(basic.get("topics")) if str(x).strip()]),
            "severity": canon("severity", basic.get("severity") or "MEDIUM"),
            "risk_min": basic.get("risk_min"),
            "locations": uniq([canon("ioc_location", x) for x in safe_list(basic.get("locations")) if str(x).strip()]),
            "labels": uniq([canon("labels", x) for x in safe_list(basic.get("labels")) if str(x).strip()]),
        },
        "ast": ast if isinstance(ast, dict) else _default_ast(),
        "meta": deepcopy(r.get("meta") or {"owner": "", "priority": 50, "desc": ""}),
        # 额外支持：显式声明标签
        "topic_id": r.get("topic_id"),
        "topic_ids": safe_list(r.get("topic_ids")),
        "topic_label": r.get("topic_label"),
        "topic_labels": safe_list(r.get("topic_labels")),
    }
    return normalized


def eval_basic(rule: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
    topics = safe_list(rule.get("basic", {}).get("topics"))
    severity = rule.get("basic", {}).get("severity") or "MEDIUM"
    risk_min = rule.get("basic", {}).get("risk_min")
    risk_min_num = None if risk_min in (None, "") else _to_number(risk_min)
    locations = safe_list(rule.get("basic", {}).get("locations"))
    labels = safe_list(rule.get("basic", {}).get("labels"))

    topic_pass = (not topics) or payload.get("threat_category") in topics
    sev_actual = payload.get("severity") or ""
    sev_pass = severity == "ALL" or SEVERITY_ORDER.get(sev_actual, -1) >= SEVERITY_ORDER.get(severity, 999)
    risk_actual = payload.get("risk_score")
    risk_pass = risk_min_num is None or (risk_actual is not None and risk_actual >= risk_min_num)
    loc_pass = (not locations) or any(canon("ioc_location", x) in safe_list(payload.get("ioc_location")) for x in locations)
    label_pass = (not labels) or any(canon("labels", x) in safe_list(payload.get("labels")) for x in labels)

    return {
        "id": new_trace_id(),
        "kind": "BASIC",
        "pass": topic_pass and sev_pass and risk_pass and loc_pass and label_pass,
        "reasons": [
            "专题命中" if topic_pass else "专题未命中",
            "等级命中" if sev_pass else "等级未命中",
            "风险分命中" if risk_pass else "风险分未命中",
            "地域命中" if loc_pass else "地域未命中",
            "标签命中" if label_pass else "标签未命中",
        ],
        "detail": {
            "topicPass": topic_pass,
            "sevPass": sev_pass,
            "riskPass": risk_pass,
            "locPass": loc_pass,
            "labelPass": label_pass,
        },
    }


def eval_cond(cond: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
    field = cond.get("field")
    cond_type = FIELD_TYPE_MAP.get(field, "string")
    op = cond.get("op")
    actual_raw = payload.get(field)

    trace: Dict[str, Any] = {
        "id": new_trace_id(),
        "kind": "COND",
        "field": field,
        "op": op,
        "expected": cond.get("value"),
        "actual": actual_raw,
        "pass": False,
        "reason": "",
    }

    if op == "exists":
        if cond_type == "array":
            trace["pass"] = isinstance(actual_raw, list) and len(actual_raw) > 0
        elif cond_type == "number":
            trace["pass"] = actual_raw is not None and isinstance(actual_raw, (int, float))
        elif cond_type == "boolean":
            trace["pass"] = isinstance(actual_raw, bool)
        else:
            trace["pass"] = actual_raw is not None and str(actual_raw).strip() != ""
        trace["reason"] = "字段存在" if trace["pass"] else "字段不存在"
        return trace

    if op == "not_exists":
        if cond_type == "array":
            trace["pass"] = not isinstance(actual_raw, list) or len(actual_raw) == 0
        elif cond_type == "number":
            trace["pass"] = actual_raw is None or not isinstance(actual_raw, (int, float))
        elif cond_type == "boolean":
            trace["pass"] = actual_raw is None
        else:
            trace["pass"] = actual_raw is None or str(actual_raw).strip() == ""
        trace["reason"] = "字段为空" if trace["pass"] else "字段不为空"
        return trace

    if op == "is_true":
        trace["pass"] = actual_raw is True
        trace["reason"] = "布尔值为 true" if trace["pass"] else "布尔值不为 true"
        return trace

    if op == "is_false":
        trace["pass"] = actual_raw is False
        trace["reason"] = "布尔值为 false" if trace["pass"] else "布尔值不为 false"
        return trace

    if op not in {"exists", "not_exists", "is_true", "is_false"} and str(cond.get("value") or "").strip() == "":
        trace["reason"] = "条件值为空"
        return trace

    if cond_type == "array":
        target = [canon(field, x) for x in safe_list(actual_raw)]
        expected = [canon(field, x) for x in csv_to_list(cond.get("value"))]
        if op == "any_of":
            trace["pass"] = any(x in target for x in expected)
        elif op == "all_of":
            trace["pass"] = all(x in target for x in expected)
        elif op == "none_of":
            trace["pass"] = all(x not in target for x in expected)
        trace["actual"] = target
        trace["reason"] = "数组条件命中" if trace["pass"] else "数组条件未命中"
        return trace

    if cond_type == "number":
        target = actual_raw if isinstance(actual_raw, (int, float)) else _to_number(actual_raw)
        value_num = _to_number(cond.get("value"))
        range_values = [_to_number(x) for x in csv_to_list(cond.get("value"))]

        if target is None:
            trace["reason"] = "实际值不是有效数字"
            return trace

        if op == "gt":
            trace["pass"] = value_num is not None and target > value_num
        elif op == "gte":
            trace["pass"] = value_num is not None and target >= value_num
        elif op == "lt":
            trace["pass"] = value_num is not None and target < value_num
        elif op == "lte":
            trace["pass"] = value_num is not None and target <= value_num
        elif op == "range":
            if len(range_values) >= 2 and range_values[0] is not None and range_values[1] is not None:
                a, b = range_values[0], range_values[1]
                trace["pass"] = min(a, b) <= target <= max(a, b)
            else:
                trace["pass"] = False
        elif op == "eq":
            trace["pass"] = value_num is not None and target == value_num
        trace["actual"] = target
        trace["reason"] = "数值条件命中" if trace["pass"] else "数值条件未命中"
        return trace

    target = canon(field, actual_raw if actual_raw is not None else "")
    expected_text = str(cond.get("value") or "").strip()
    expected_canon = canon(field, expected_text)
    expected_list = [canon(field, x) for x in csv_to_list(cond.get("value"))]

    if op == "eq":
        trace["pass"] = str(target) == str(expected_canon)
    elif op == "contains":
        trace["pass"] = str(expected_canon) in str(target)
    elif op == "in_list":
        trace["pass"] = str(target) in [str(x) for x in expected_list]
    elif op == "not_in_list":
        trace["pass"] = str(target) not in [str(x) for x in expected_list]
    elif op == "regex":
        try:
            if len(expected_text) > APP["regex_max_len"]:
                trace["reason"] = f"正则超长（>{APP['regex_max_len']}）"
                return trace
            trace["pass"] = re.search(expected_text, str(target), flags=re.IGNORECASE) is not None
        except re.error as exc:
            trace["reason"] = f"正则错误：{exc}"
            return trace

    trace["actual"] = target
    trace["reason"] = "字符串条件命中" if trace["pass"] else "字符串条件未命中"
    return trace


def eval_ast(node: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(node, dict):
        return {"id": new_trace_id(), "kind": "ERROR", "pass": False, "reason": "AST 节点非法"}

    node_type = node.get("type")
    if node_type == "COND":
        return eval_cond(node, payload)

    if node_type == "GROUP":
        children = [eval_ast(child, payload) for child in safe_list(node.get("children"))]
        trace = {
            "id": new_trace_id(),
            "kind": "GROUP",
            "op": node.get("op"),
            "children": children,
            "pass": False,
            "reason": "",
        }

        if node.get("op") == "NOT":
            first = children[0] if children else None
            trace["pass"] = (not first["pass"]) if first else False
            trace["reason"] = "NOT 反转后命中" if trace["pass"] else "NOT 反转后未命中"
            return trace

        if not children:
            trace["reason"] = "空分组不允许命中"
            return trace

        if node.get("op") == "AND":
            trace["pass"] = all(child.get("pass") for child in children)
            trace["reason"] = "AND 全部命中" if trace["pass"] else "AND 存在未命中条件"
        elif node.get("op") == "OR":
            trace["pass"] = any(child.get("pass") for child in children)
            trace["reason"] = "OR 至少一个命中" if trace["pass"] else "OR 全部未命中"
        else:
            trace["reason"] = "未知分组操作符"
        return trace

    return {"id": new_trace_id(), "kind": "ERROR", "pass": False, "reason": "未知 AST 节点类型"}


def flatten_trace_reasons(trace: Dict[str, Any], out: Optional[List[str]] = None) -> List[str]:
    out = out or []
    if not isinstance(trace, dict):
        return out
    if trace.get("kind") == "COND":
        out.append(f"{trace.get('field')} / {trace.get('op')} / {'命中' if trace.get('pass') else '未命中'} / {trace.get('reason')}")
    elif trace.get("kind") == "GROUP":
        out.append(f"{trace.get('op')} / {'命中' if trace.get('pass') else '未命中'} / {trace.get('reason')}")
        for child in safe_list(trace.get("children")):
            flatten_trace_reasons(child, out)
    elif trace.get("reason"):
        out.append(str(trace["reason"]))
    return out


def _collect_positive_topics(node: Dict[str, Any], negated: bool = False) -> List[str]:
    if not isinstance(node, dict):
        return []

    node_type = node.get("type")
    if node_type == "GROUP":
        if node.get("op") == "NOT":
            children = safe_list(node.get("children"))
            return _collect_positive_topics(children[0], not negated) if children else []
        topics: List[str] = []
        for child in safe_list(node.get("children")):
            topics.extend(_collect_positive_topics(child, negated))
        return uniq(topics)

    if node_type == "COND":
        if negated:
            return []
        if node.get("field") != "threat_category":
            return []
        op = node.get("op")
        if op == "eq":
            value = str(node.get("value") or "").strip()
            return [value] if value else []
        if op == "in_list":
            return [item for item in csv_to_list(node.get("value")) if item]
    return []


def infer_topics_from_rule(rule: Dict[str, Any]) -> Tuple[List[str], List[str]]:
    topic_ids: List[str] = []
    topic_labels: List[str] = []

    explicit_ids = []
    if rule.get("topic_id"):
        explicit_ids.append(str(rule["topic_id"]).strip())
    explicit_ids.extend(str(x).strip() for x in safe_list(rule.get("topic_ids")) if str(x).strip())
    topic_ids.extend(explicit_ids)

    if rule.get("topic_label"):
        topic_labels.append(str(rule["topic_label"]).strip())
    topic_labels.extend(str(x).strip() for x in safe_list(rule.get("topic_labels")) if str(x).strip())

    basic_topics = [str(x).strip() for x in safe_list(rule.get("basic", {}).get("topics")) if str(x).strip()]
    topic_ids.extend(basic_topics)

    topic_ids.extend(_collect_positive_topics(rule.get("ast"), negated=False))

    topic_ids = uniq([x for x in topic_ids if x])
    topic_labels.extend(TOPIC_NAME_MAP.get(topic_id, topic_id) for topic_id in topic_ids)
    topic_labels = uniq([x for x in topic_labels if x])
    return topic_ids, topic_labels


class TopicRuleEngine:
    def __init__(self, rules: List[Dict[str, Any]]) -> None:
        self.rules: List[Dict[str, Any]] = [normalize_rule(rule) for rule in safe_list(rules)]

    @classmethod
    def from_json_file(cls, path: str | Path) -> "TopicRuleEngine":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if isinstance(data, dict) and isinstance(data.get("rules"), list):
            rules = data["rules"]
        elif isinstance(data, list):
            rules = data
        else:
            raise ValueError("规则文件格式不正确：应为 rule 列表，或包含 rules 列表的对象")
        return cls(rules)

    def validate_rules(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": rule["id"],
                "name": rule["name"],
                **validate_rule(rule),
            }
            for rule in self.rules
        ]

    def _resolve_topics_for_hit(self, rule: Dict[str, Any], payload: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        inferred_ids, inferred_labels = infer_topics_from_rule(rule)
        event_topic = str(payload.get("threat_category") or "").strip()

        topic_ids = list(inferred_ids)
        topic_labels = list(inferred_labels)

        if event_topic:
            if topic_ids:
                if event_topic in topic_ids:
                    topic_ids = [event_topic]
                    topic_labels = [TOPIC_NAME_MAP.get(event_topic, event_topic)]
            else:
                topic_ids = [event_topic]
                topic_labels = [TOPIC_NAME_MAP.get(event_topic, event_topic)]

        return uniq(topic_ids), uniq(topic_labels)

    def _match_rule_with_payload(self, rule: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
        if not rule.get("enabled", True):
            return {
                "rule_id": rule["id"],
                "rule_name": rule["name"],
                "enabled": False,
                "matched": False,
                "trace": {"kind": "RULE", "pass": False, "reason": "规则已停用"},
                "topic_ids": [],
                "topic_labels": [],
            }

        if rule.get("mode") == "basic":
            trace = eval_basic(rule, payload)
            reasons = trace.get("reasons", [])
        else:
            trace = eval_ast(rule.get("ast"), payload)
            reasons = flatten_trace_reasons(trace)

        matched = bool(trace.get("pass"))
        topic_ids, topic_labels = self._resolve_topics_for_hit(rule, payload) if matched else ([], [])

        return {
            "rule_id": rule["id"],
            "rule_name": rule["name"],
            "enabled": True,
            "mode": rule.get("mode"),
            "matched": matched,
            "trace": trace,
            "reasons": reasons,
            "topic_ids": topic_ids,
            "topic_labels": topic_labels,
        }

    def match_rule(self, rule: Dict[str, Any], message: Dict[str, Any]) -> Dict[str, Any]:
        payload = normalize_engine_output(message)
        return self._match_rule_with_payload(normalize_rule(rule), payload)

    def tag_message(self, message: Dict[str, Any], include_non_matches: bool = False) -> Dict[str, Any]:
        payload = normalize_engine_output(message)
        matched_rules: List[Dict[str, Any]] = []
        unmatched_rules: List[Dict[str, Any]] = []
        topic_ids: List[str] = []
        topic_labels: List[str] = []

        for rule in self.rules:
            result = self._match_rule_with_payload(rule, payload)
            if result["matched"]:
                matched_rules.append(result)
                topic_ids.extend(result["topic_ids"])
                topic_labels.extend(result["topic_labels"])
            elif include_non_matches:
                unmatched_rules.append(result)

        topic_ids = uniq(topic_ids)
        topic_labels = uniq(topic_labels)

        return {
            "event": payload,
            "matched": bool(matched_rules),
            "topic_ids": topic_ids,
            "topic_labels": topic_labels,
            "matched_rules": matched_rules,
            "unmatched_rules": unmatched_rules if include_non_matches else [],
        }

    def tag_messages(self, messages: List[Dict[str, Any]], include_non_matches: bool = False) -> List[Dict[str, Any]]:
        return [self.tag_message(message, include_non_matches=include_non_matches) for message in safe_list(messages)]


def build_example_rules() -> Dict[str, Any]:
    return {
        "schema_version": APP["schema"],
        "adapter_version": APP["adapter"],
        "rules": [
            {
                "id": "rule_drugs_ast_01",
                "name": "高危涉毒 Telegram AST 规则",
                "enabled": True,
                "status": "applied",
                "mode": "ast",
                "meta": {
                    "owner": "SystemAdmin",
                    "priority": 80,
                    "desc": "命中后打上涉毒专题标签",
                },
                "ast": {
                    "type": "GROUP",
                    "op": "AND",
                    "children": [
                        {
                            "type": "COND",
                            "field": "threat_category",
                            "op": "eq",
                            "value": "TopicDrugs",
                        },
                        {
                            "type": "GROUP",
                            "op": "OR",
                            "children": [
                                {
                                    "type": "COND",
                                    "field": "severity",
                                    "op": "in_list",
                                    "value": "HIGH,CRITICAL",
                                },
                                {
                                    "type": "COND",
                                    "field": "risk_score",
                                    "op": "gte",
                                    "value": "80",
                                },
                            ],
                        },
                        {
                            "type": "COND",
                            "field": "source_platform",
                            "op": "eq",
                            "value": "Telegram",
                        },
                        {
                            "type": "COND",
                            "field": "labels",
                            "op": "any_of",
                            "value": "贩毒,暗网担保",
                        },
                    ],
                },
            }
        ],
    }


def build_example_messages() -> List[Dict[str, Any]]:
    return [
        {
            "threat_category": "TopicDrugs",
            "severity": "HIGH",
            "risk_score": 85,
            "source_platform": "Telegram",
            "source_handle": "drug_01",
            "labels": ["贩毒", "暗网担保"],
            "raw_content": "新到一批纯白，支持USDT担保。",
            "entity_type": "wallet",
            "entity_value": "TXYZ...123",
            "extracted_iocs": {
                "location": ["缅北"],
                "crypto": ["USDT"],
            },
        },
        {
            "threat_category": "TopicDataLeak",
            "severity": "LOW",
            "risk_score": 20,
            "source_platform": "Forum",
            "labels": ["无关标签"],
            "raw_content": "普通讨论内容。",
        },
    ]


def _cli() -> None:
    parser = argparse.ArgumentParser(description="根据 config.html 专家 AST 模式实现的专题标签引擎")
    parser.add_argument("--rules", help="规则文件路径。支持导出配置对象{rules:[...]}或纯规则数组")
    parser.add_argument("--input", help="输入消息 JSON 文件路径。支持单条对象或对象数组")
    parser.add_argument("--include-non-matches", action="store_true", help="输出未命中规则详情")
    parser.add_argument("--validate", action="store_true", help="只校验规则，不执行打标")
    parser.add_argument("--write-example-rules", help="把示例规则写到指定路径")
    parser.add_argument("--write-example-input", help="把示例输入写到指定路径")
    args = parser.parse_args()

    if args.write_example_rules:
        Path(args.write_example_rules).write_text(
            json.dumps(build_example_rules(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"示例规则已写入: {args.write_example_rules}")
        return

    if args.write_example_input:
        Path(args.write_example_input).write_text(
            json.dumps(build_example_messages(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"示例输入已写入: {args.write_example_input}")
        return

    if not args.rules:
        parser.error("必须提供 --rules，或使用 --write-example-rules 先生成示例")

    engine = TopicRuleEngine.from_json_file(args.rules)

    if args.validate:
        print(json.dumps(engine.validate_rules(), ensure_ascii=False, indent=2))
        return

    if not args.input:
        parser.error("执行打标时必须提供 --input")

    raw_input = json.loads(Path(args.input).read_text(encoding="utf-8"))
    messages = raw_input if isinstance(raw_input, list) else [raw_input]
    result = engine.tag_messages(messages, include_non_matches=args.include_non_matches)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    _cli()
