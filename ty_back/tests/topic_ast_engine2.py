from __future__ import annotations

import argparse
import json
import re
import time
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Pattern, Sequence, Tuple, Union


APP = {
    "schema": "router_gw_v15.0",
    "adapter": "2.0",
    "regex_max_len": 200,
    "ast_max_depth": 20,
    "trace_reason_limit": 50,
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

COMMON_OPS = {"exists", "not_exists"}
OPS_BY_TYPE: Dict[str, set[str]] = {
    "string": COMMON_OPS | {"eq", "contains", "in_list", "not_in_list", "regex"},
    "number": COMMON_OPS | {"gt", "gte", "lt", "lte", "range", "eq"},
    "array": COMMON_OPS | {"any_of", "all_of", "none_of"},
    "boolean": COMMON_OPS | {"is_true", "is_false"},
}
TRACE_LEVELS = {"none", "summary", "full"}


def safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def uniq(seq: Sequence[Any]) -> List[Any]:
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
    return f"tr_{time.time_ns():x}"


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

    out["content_hash"] = stable_hash(out["raw_content"] or json.dumps(r, ensure_ascii=False, sort_keys=True)[:2000])

    timestamp = r.get("timestamp", r.get("event_time", r.get("time")))
    if isinstance(timestamp, (int, float)):
        out["event_time"] = int(timestamp)
        out["event_time_parse_error"] = None
    elif isinstance(timestamp, str):
        try:
            out["event_time"] = int(__import__("datetime").datetime.fromisoformat(timestamp.replace("Z", "+00:00")).timestamp() * 1000)
            out["event_time_parse_error"] = None
        except ValueError:
            out["event_time"] = None
            out["event_time_parse_error"] = f"无法解析时间: {timestamp}"
    else:
        out["event_time"] = None
        out["event_time_parse_error"] = None

    for field_name in ("ioc_location", "ioc_crypto", "ioc_url", "ioc_phone", "ioc_email"):
        out[field_name] = uniq([canon(field_name, item) for item in safe_list(out[field_name]) if item not in (None, "")])

    return out


def walk_ast(node: Optional[Dict[str, Any]], cb, depth: int = 1) -> None:
    if not isinstance(node, dict):
        return
    cb(node, depth)
    for child in safe_list(node.get("children")):
        walk_ast(child, cb, depth + 1)


def count_ast_conditions(node: Optional[Dict[str, Any]]) -> int:
    if not isinstance(node, dict):
        return 0
    if node.get("type") == "COND":
        return 1
    return sum(count_ast_conditions(child) for child in safe_list(node.get("children")))


def has_empty_ast_root(rule: Dict[str, Any]) -> bool:
    return rule.get("mode") == "ast" and (not isinstance(rule.get("ast"), dict) or not safe_list(rule["ast"].get("children")))


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

    meta = deepcopy(r.get("meta") or {})
    priority = meta.get("priority", 50)
    try:
        priority = int(priority)
    except (TypeError, ValueError):
        priority = priority

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
        "meta": {
            "owner": meta.get("owner", ""),
            "priority": priority,
            "desc": meta.get("desc", ""),
        },
        "topic_id": r.get("topic_id"),
        "topic_ids": safe_list(r.get("topic_ids")),
        "topic_label": r.get("topic_label"),
        "topic_labels": safe_list(r.get("topic_labels")),
    }
    return normalized


@dataclass
class ValidationResult:
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


@dataclass(frozen=True)
class CompiledCond:
    raw: Dict[str, Any]
    field: str
    field_type: str
    op: str
    value: Any
    regex: Optional[Pattern[str]] = None


@dataclass(frozen=True)
class CompiledGroup:
    raw: Dict[str, Any]
    op: str
    children: Tuple["CompiledNode", ...]


CompiledNode = Union[CompiledCond, CompiledGroup]


@dataclass
class CompiledRule:
    rule: Dict[str, Any]
    priority: int
    validation: ValidationResult
    compiled_match: Optional[CompiledNode]
    explicit_topic_ids: List[str]
    explicit_topic_labels: List[str]
    compile_error: Optional[str] = None

    @property
    def is_valid(self) -> bool:
        return self.compile_error is None and self.validation.ok


def _validate_basic_config(rule: Dict[str, Any], result: ValidationResult) -> None:
    basic = rule.get("basic", {})
    severity = str(basic.get("severity") or "MEDIUM").upper()
    if severity not in SEVERITY_ORDER:
        result.errors.append(f"basic.severity 非法: {severity}")

    risk_min = basic.get("risk_min")
    if risk_min not in (None, "") and _to_number(risk_min) is None:
        result.errors.append("basic.risk_min 必须是数值")

    for field_name in ("topics", "locations", "labels"):
        value = basic.get(field_name)
        if value is not None and not isinstance(value, list):
            result.errors.append(f"basic.{field_name} 必须是数组")


def _validate_ast_node(node: Any, result: ValidationResult, path: str, depth: int) -> None:
    if depth > APP["ast_max_depth"]:
        result.errors.append(f"{path} 超过 AST 最大深度 {APP['ast_max_depth']}")
        return

    if not isinstance(node, dict):
        result.errors.append(f"{path} 不是合法对象")
        return

    node_type = node.get("type")
    if node_type not in {"GROUP", "COND"}:
        result.errors.append(f"{path}.type 非法: {node_type}")
        return

    if node_type == "GROUP":
        op = node.get("op")
        if op not in {"AND", "OR", "NOT"}:
            result.errors.append(f"{path}.op 非法: {op}")
            return

        children = node.get("children")
        if not isinstance(children, list):
            result.errors.append(f"{path}.children 必须是数组")
            return

        if not children:
            result.errors.append(f"{path} 为空分组，不允许")
            return

        if op == "NOT" and len(children) != 1:
            result.errors.append(f"{path} 的 NOT 分组必须且只能有 1 个子节点")
            return

        for idx, child in enumerate(children):
            _validate_ast_node(child, result, f"{path}.children[{idx}]", depth + 1)
        return

    field_name = node.get("field")
    op = node.get("op")
    value = node.get("value")

    if field_name not in FIELD_TYPE_MAP:
        result.errors.append(f"{path}.field 非法: {field_name}")
        return

    field_type = FIELD_TYPE_MAP[field_name]
    allowed_ops = OPS_BY_TYPE[field_type]
    if op not in allowed_ops:
        result.errors.append(f"{path}.op 非法: {op}，字段 {field_name} 类型为 {field_type}")
        return

    if op not in {"exists", "not_exists", "is_true", "is_false"} and str(value or "").strip() == "":
        result.errors.append(f"{path}.value 不能为空")
        return

    if field_type == "number":
        if op in {"gt", "gte", "lt", "lte", "eq"} and _to_number(value) is None:
            result.errors.append(f"{path}.value 必须是有效数字")
        elif op == "range":
            parts = csv_to_list(value)
            if len(parts) != 2 or any(_to_number(part) is None for part in parts):
                result.errors.append(f"{path}.value 必须是两个有效数字，格式如 10,20")

    if field_type == "boolean" and op not in {"exists", "not_exists", "is_true", "is_false"}:
        result.errors.append(f"{path}.op 非法: 布尔字段仅支持 exists/not_exists/is_true/is_false")

    if op == "regex":
        pattern = str(value or "")
        if len(pattern) > APP["regex_max_len"]:
            result.errors.append(f"{path}.value 正则长度超过限制 {APP['regex_max_len']}")
        elif len(pattern) > 100:
            result.warnings.append(f"{path}.value 正则较长，可能存在性能风险")
        try:
            re.compile(pattern, flags=re.IGNORECASE)
        except re.error as exc:
            result.errors.append(f"{path}.value 正则语法错误: {exc}")


def validate_rule(rule: Dict[str, Any], known_rule_ids: Optional[set[str]] = None) -> Dict[str, List[str]]:
    normalized = normalize_rule(rule)
    result = ValidationResult()

    if not str(normalized.get("name") or "").strip():
        result.errors.append("规则名称不能为空")

    rule_id = str(normalized.get("id") or "").strip()
    if not rule_id:
        result.errors.append("规则 ID 不能为空")
    elif known_rule_ids is not None:
        if rule_id in known_rule_ids:
            result.errors.append(f"规则 ID 重复: {rule_id}")
        else:
            known_rule_ids.add(rule_id)

    priority = normalized.get("meta", {}).get("priority", 50)
    if not isinstance(priority, int) or not 1 <= priority <= 100:
        result.errors.append("规则优先级必须是 1 到 100 之间的整数")

    if normalized.get("mode") == "ast":
        if has_empty_ast_root(normalized):
            result.errors.append("AST 专家模式下，根条件组为空")
        else:
            _validate_ast_node(normalized.get("ast"), result, "ast", 1)
    elif normalized.get("mode") == "basic":
        _validate_basic_config(normalized, result)
    else:
        result.errors.append(f"未知规则模式: {normalized.get('mode')}")

    return {"errors": result.errors, "warnings": result.warnings}


def _compile_ast(node: Dict[str, Any], regex_cache: Dict[str, Pattern[str]]) -> CompiledNode:
    if not isinstance(node, dict):
        raise ValueError("AST 节点非法：不是对象")

    node_type = node.get("type")
    if node_type == "GROUP":
        op = node.get("op")
        if op not in {"AND", "OR", "NOT"}:
            raise ValueError(f"未知分组操作符: {op}")
        children = node.get("children")
        if not isinstance(children, list):
            raise ValueError("GROUP.children 必须是数组")
        if op == "NOT" and len(children) != 1:
            raise ValueError("NOT 分组必须且只能有 1 个子节点")
        if not children:
            raise ValueError("空分组不允许")
        return CompiledGroup(
            raw=node,
            op=op,
            children=tuple(_compile_ast(child, regex_cache) for child in children),
        )

    if node_type != "COND":
        raise ValueError(f"未知 AST 节点类型: {node_type}")

    field_name = node.get("field")
    op = node.get("op")
    if field_name not in FIELD_TYPE_MAP:
        raise ValueError(f"非法字段: {field_name}")

    field_type = FIELD_TYPE_MAP[field_name]
    if op not in OPS_BY_TYPE[field_type]:
        raise ValueError(f"非法操作符: {op}，字段 {field_name} 类型为 {field_type}")

    regex_obj = None
    if op == "regex":
        pattern = str(node.get("value") or "")
        regex_obj = regex_cache.get(pattern)
        if regex_obj is None:
            regex_obj = re.compile(pattern, flags=re.IGNORECASE)
            regex_cache[pattern] = regex_obj

    return CompiledCond(
        raw=node,
        field=field_name,
        field_type=field_type,
        op=op,
        value=node.get("value"),
        regex=regex_obj,
    )


def _extract_explicit_topics(rule: Dict[str, Any]) -> Tuple[List[str], List[str]]:
    topic_ids: List[str] = []
    topic_labels: List[str] = []

    if rule.get("topic_id"):
        topic_ids.append(str(rule["topic_id"]).strip())
    topic_ids.extend(str(x).strip() for x in safe_list(rule.get("topic_ids")) if str(x).strip())

    if rule.get("topic_label"):
        topic_labels.append(str(rule["topic_label"]).strip())
    topic_labels.extend(str(x).strip() for x in safe_list(rule.get("topic_labels")) if str(x).strip())

    topic_labels.extend(TOPIC_NAME_MAP.get(topic_id, topic_id) for topic_id in topic_ids)
    return uniq([x for x in topic_ids if x]), uniq([x for x in topic_labels if x])


def compile_rule(rule: Dict[str, Any], regex_cache: Optional[Dict[str, Pattern[str]]] = None) -> CompiledRule:
    normalized = normalize_rule(rule)
    validation_dict = validate_rule(normalized)
    validation = ValidationResult(
        errors=list(validation_dict["errors"]),
        warnings=list(validation_dict["warnings"]),
    )
    explicit_ids, explicit_labels = _extract_explicit_topics(normalized)

    priority = normalized.get("meta", {}).get("priority", 50)
    priority = priority if isinstance(priority, int) else 50

    if not validation.ok:
        return CompiledRule(
            rule=normalized,
            priority=priority,
            validation=validation,
            compiled_match=None,
            explicit_topic_ids=explicit_ids,
            explicit_topic_labels=explicit_labels,
            compile_error="规则校验未通过",
        )

    try:
        compiled_match = None
        if normalized.get("mode") == "ast":
            compiled_match = _compile_ast(normalized["ast"], {} if regex_cache is None else regex_cache)
        return CompiledRule(
            rule=normalized,
            priority=priority,
            validation=validation,
            compiled_match=compiled_match,
            explicit_topic_ids=explicit_ids,
            explicit_topic_labels=explicit_labels,
        )
    except Exception as exc:
        validation.errors.append(str(exc))
        return CompiledRule(
            rule=normalized,
            priority=priority,
            validation=validation,
            compiled_match=None,
            explicit_topic_ids=explicit_ids,
            explicit_topic_labels=explicit_labels,
            compile_error=str(exc),
        )


def _error_trace(reason: str, **extra: Any) -> Dict[str, Any]:
    out = {"id": new_trace_id(), "kind": "ERROR", "pass": False, "reason": reason}
    out.update(extra)
    return out


def eval_basic(compiled_rule: CompiledRule, payload: Dict[str, Any]) -> Dict[str, Any]:
    rule = compiled_rule.rule
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

    matched_topics: List[str] = []
    if topic_pass and topics:
        actual_topic = str(payload.get("threat_category") or "").strip()
        if actual_topic:
            matched_topics.append(actual_topic)

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
        "matched_topics": uniq(matched_topics),
    }


def eval_cond(cond: CompiledCond, payload: Dict[str, Any]) -> Dict[str, Any]:
    field_name = cond.field
    cond_type = cond.field_type
    op = cond.op
    actual_raw = payload.get(field_name)

    trace: Dict[str, Any] = {
        "id": new_trace_id(),
        "kind": "COND",
        "field": field_name,
        "op": op,
        "expected": cond.value,
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

    if op not in {"exists", "not_exists", "is_true", "is_false"} and str(cond.value or "").strip() == "":
        return _error_trace("条件值为空", field=field_name, op=op, actual=actual_raw)

    if cond_type == "array":
        if op not in {"any_of", "all_of", "none_of"}:
            return _error_trace(f"非法数组操作符: {op}", field=field_name, op=op, actual=actual_raw)
        target = [canon(field_name, x) for x in safe_list(actual_raw)]
        expected = [canon(field_name, x) for x in csv_to_list(cond.value)]
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
        if op not in {"gt", "gte", "lt", "lte", "range", "eq"}:
            return _error_trace(f"非法数值操作符: {op}", field=field_name, op=op, actual=actual_raw)
        target = actual_raw if isinstance(actual_raw, (int, float)) else _to_number(actual_raw)
        value_num = _to_number(cond.value)
        range_values = [_to_number(x) for x in csv_to_list(cond.value)]

        if target is None:
            return _error_trace("实际值不是有效数字", field=field_name, op=op, actual=actual_raw)

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
                return _error_trace("range 条件值非法", field=field_name, op=op, actual=actual_raw)
        elif op == "eq":
            trace["pass"] = value_num is not None and target == value_num
        trace["actual"] = target
        trace["reason"] = "数值条件命中" if trace["pass"] else "数值条件未命中"
        return trace

    if cond_type != "string":
        return _error_trace(f"未支持的字段类型: {cond_type}", field=field_name, op=op, actual=actual_raw)

    if op not in {"eq", "contains", "in_list", "not_in_list", "regex"}:
        return _error_trace(f"非法字符串操作符: {op}", field=field_name, op=op, actual=actual_raw)

    target = canon(field_name, actual_raw if actual_raw is not None else "")
    expected_text = str(cond.value or "").strip()
    expected_canon = canon(field_name, expected_text)
    expected_list = [canon(field_name, x) for x in csv_to_list(cond.value)]

    if op == "eq":
        trace["pass"] = str(target) == str(expected_canon)
    elif op == "contains":
        trace["pass"] = str(expected_canon) in str(target)
    elif op == "in_list":
        trace["pass"] = str(target) in [str(x) for x in expected_list]
    elif op == "not_in_list":
        trace["pass"] = str(target) not in [str(x) for x in expected_list]
    elif op == "regex":
        if cond.regex is None:
            return _error_trace("正则未预编译", field=field_name, op=op, actual=actual_raw)
        trace["pass"] = cond.regex.search(str(target)) is not None

    trace["actual"] = target
    trace["reason"] = "字符串条件命中" if trace["pass"] else "字符串条件未命中"

    if trace["pass"] and field_name == "threat_category":
        if op == "eq" and expected_canon:
            trace["matched_topics"] = [str(expected_canon)]
        elif op == "in_list" and target:
            trace["matched_topics"] = [str(target)]
    return trace


def eval_ast(node: CompiledNode, payload: Dict[str, Any], short_circuit: bool = True) -> Dict[str, Any]:
    if isinstance(node, CompiledCond):
        return eval_cond(node, payload)

    children_traces: List[Dict[str, Any]] = []
    trace: Dict[str, Any] = {
        "id": new_trace_id(),
        "kind": "GROUP",
        "op": node.op,
        "children": children_traces,
        "pass": False,
        "reason": "",
    }

    if node.op == "NOT":
        child_trace = eval_ast(node.children[0], payload, short_circuit=short_circuit)
        children_traces.append(child_trace)
        trace["pass"] = not bool(child_trace.get("pass"))
        trace["reason"] = "NOT 反转后命中" if trace["pass"] else "NOT 反转后未命中"
        return trace

    if node.op == "AND":
        any_error = False
        for child in node.children:
            child_trace = eval_ast(child, payload, short_circuit=short_circuit)
            children_traces.append(child_trace)
            if child_trace.get("kind") == "ERROR":
                any_error = True
                if short_circuit:
                    break
            elif not child_trace.get("pass"):
                if short_circuit:
                    break
        if any_error:
            trace["kind"] = "ERROR"
            trace["reason"] = "AND 子条件执行出错"
            trace["pass"] = False
            return trace
        trace["pass"] = all(child.get("pass") for child in children_traces) and len(children_traces) == len(node.children)
        trace["reason"] = "AND 全部命中" if trace["pass"] else "AND 存在未命中条件"
        return trace

    if node.op == "OR":
        any_error = False
        any_pass = False
        for child in node.children:
            child_trace = eval_ast(child, payload, short_circuit=short_circuit)
            children_traces.append(child_trace)
            if child_trace.get("kind") == "ERROR":
                any_error = True
                if short_circuit:
                    break
            elif child_trace.get("pass"):
                any_pass = True
                if short_circuit:
                    break
        if any_error:
            trace["kind"] = "ERROR"
            trace["reason"] = "OR 子条件执行出错"
            trace["pass"] = False
            return trace
        trace["pass"] = any_pass if short_circuit else any(child.get("pass") for child in children_traces)
        trace["reason"] = "OR 至少一个命中" if trace["pass"] else "OR 全部未命中"
        return trace

    return _error_trace(f"未知分组操作符: {node.op}")


def flatten_trace_reasons(trace: Dict[str, Any], out: Optional[List[str]] = None, limit: int = APP["trace_reason_limit"]) -> List[str]:
    out = out or []
    if not isinstance(trace, dict) or len(out) >= limit:
        return out
    if trace.get("kind") == "COND":
        out.append(f"{trace.get('field')} / {trace.get('op')} / {'命中' if trace.get('pass') else '未命中'} / {trace.get('reason')}")
    elif trace.get("kind") == "GROUP":
        out.append(f"{trace.get('op')} / {'命中' if trace.get('pass') else '未命中'} / {trace.get('reason')}")
        for child in safe_list(trace.get("children")):
            flatten_trace_reasons(child, out, limit=limit)
            if len(out) >= limit:
                break
    elif trace.get("reason"):
        out.append(str(trace["reason"]))
    return out


def _collect_topics_from_trace(trace: Dict[str, Any], negated: bool = False) -> List[str]:
    if not isinstance(trace, dict):
        return []

    kind = trace.get("kind")
    if kind == "GROUP":
        op = trace.get("op")
        children = safe_list(trace.get("children"))
        if op == "NOT":
            return _collect_topics_from_trace(children[0], not negated) if children else []
        topics: List[str] = []
        for child in children:
            topics.extend(_collect_topics_from_trace(child, negated))
        return uniq(topics)

    if kind == "COND":
        if negated or not trace.get("pass"):
            return []
        matched_topics = trace.get("matched_topics")
        return uniq([str(x).strip() for x in safe_list(matched_topics) if str(x).strip()])

    if kind == "BASIC":
        if negated or not trace.get("pass"):
            return []
        return uniq([str(x).strip() for x in safe_list(trace.get("matched_topics")) if str(x).strip()])

    return []


def _topic_labels_from_ids(topic_ids: Sequence[str]) -> List[str]:
    return uniq([TOPIC_NAME_MAP.get(topic_id, topic_id) for topic_id in topic_ids if topic_id])


def _summarize_trace(trace: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(trace, dict):
        return {"kind": "ERROR", "pass": False, "reason": "trace 非法"}

    reasons = flatten_trace_reasons(trace)
    return {
        "kind": trace.get("kind"),
        "pass": bool(trace.get("pass")),
        "reason": trace.get("reason"),
        "reasons": reasons,
    }


class TopicRuleEngine:
    def __init__(
        self,
        rules: List[Dict[str, Any]],
        *,
        short_circuit: bool = True,
        default_trace_level: str = "summary",
        stop_on_first_match: bool = False,
    ) -> None:
        if default_trace_level not in TRACE_LEVELS:
            raise ValueError(f"trace_level 非法: {default_trace_level}")

        self.short_circuit = short_circuit
        self.default_trace_level = default_trace_level
        self.stop_on_first_match = stop_on_first_match
        self.regex_cache: Dict[str, Pattern[str]] = {}
        self.compiled_rules: List[CompiledRule] = []
        self.rule_index: Dict[str, CompiledRule] = {}

        known_ids: set[str] = set()
        for rule in safe_list(rules):
            normalized = normalize_rule(rule)
            validation_dict = validate_rule(normalized, known_rule_ids=known_ids)
            validation = ValidationResult(
                errors=list(validation_dict["errors"]),
                warnings=list(validation_dict["warnings"]),
            )
            explicit_ids, explicit_labels = _extract_explicit_topics(normalized)
            priority = normalized.get("meta", {}).get("priority", 50)
            priority = priority if isinstance(priority, int) else 50

            compile_error: Optional[str] = None
            compiled_match: Optional[CompiledNode] = None

            if validation.ok:
                try:
                    if normalized.get("mode") == "ast":
                        compiled_match = _compile_ast(normalized["ast"], self.regex_cache)
                except Exception as exc:
                    compile_error = str(exc)
                    validation.errors.append(str(exc))
            else:
                compile_error = "规则校验未通过"

            compiled_rule = CompiledRule(
                rule=normalized,
                priority=priority,
                validation=validation,
                compiled_match=compiled_match,
                explicit_topic_ids=explicit_ids,
                explicit_topic_labels=explicit_labels,
                compile_error=compile_error,
            )
            self.compiled_rules.append(compiled_rule)
            self.rule_index[normalized["id"]] = compiled_rule

        self.compiled_rules.sort(key=lambda item: (-item.priority, str(item.rule["id"])))

    @classmethod
    def from_json_file(cls, path: str | Path, **kwargs: Any) -> "TopicRuleEngine":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if isinstance(data, dict) and isinstance(data.get("rules"), list):
            rules = data["rules"]
        elif isinstance(data, list):
            rules = data
        else:
            raise ValueError("规则文件格式不正确：应为 rule 列表，或包含 rules 列表的对象")
        return cls(rules, **kwargs)

    def validate_rules(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": compiled.rule["id"],
                "name": compiled.rule["name"],
                "priority": compiled.priority,
                "valid": compiled.is_valid,
                "errors": compiled.validation.errors,
                "warnings": compiled.validation.warnings,
            }
            for compiled in self.compiled_rules
        ]

    def _resolve_topics_for_hit(self, compiled_rule: CompiledRule, trace: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        trace_topics = _collect_topics_from_trace(trace)
        topic_ids = uniq([*compiled_rule.explicit_topic_ids, *trace_topics])
        topic_labels = uniq([*compiled_rule.explicit_topic_labels, *_topic_labels_from_ids(trace_topics)])
        return topic_ids, topic_labels

    def _render_trace(
        self,
        trace: Dict[str, Any],
        *,
        trace_level: str,
    ) -> Tuple[Optional[Dict[str, Any]], List[str]]:
        if trace_level == "none":
            return None, []
        if trace_level == "summary":
            summary = _summarize_trace(trace)
            return summary, summary.get("reasons", [])
        return trace, flatten_trace_reasons(trace)

    def _match_compiled_rule_with_payload(
        self,
        compiled_rule: CompiledRule,
        payload: Dict[str, Any],
        *,
        trace_level: str,
        short_circuit: bool,
    ) -> Dict[str, Any]:
        base_result = {
            "rule_id": compiled_rule.rule["id"],
            "rule_name": compiled_rule.rule["name"],
            "priority": compiled_rule.priority,
            "enabled": bool(compiled_rule.rule.get("enabled", True)),
            "mode": compiled_rule.rule.get("mode"),
            "matched": False,
            "topic_ids": [],
            "topic_labels": [],
            "trace": None,
            "reasons": [],
        }

        if not compiled_rule.rule.get("enabled", True):
            trace = {"kind": "RULE", "pass": False, "reason": "规则已停用"}
            rendered_trace, reasons = self._render_trace(trace, trace_level=trace_level)
            base_result.update({"trace": rendered_trace, "reasons": reasons})
            return base_result

        if not compiled_rule.is_valid:
            trace = _error_trace(compiled_rule.compile_error or "规则不可执行")
            rendered_trace, reasons = self._render_trace(trace, trace_level=trace_level)
            base_result.update({"trace": rendered_trace, "reasons": reasons, "error": compiled_rule.compile_error})
            return base_result

        if compiled_rule.rule.get("mode") == "basic":
            trace = eval_basic(compiled_rule, payload)
        else:
            if compiled_rule.compiled_match is None:
                trace = _error_trace("规则未编译")
            else:
                trace = eval_ast(compiled_rule.compiled_match, payload, short_circuit=short_circuit)

        matched = bool(trace.get("pass")) and trace.get("kind") != "ERROR"
        topic_ids, topic_labels = self._resolve_topics_for_hit(compiled_rule, trace) if matched else ([], [])

        rendered_trace, reasons = self._render_trace(trace, trace_level=trace_level)
        base_result.update(
            {
                "matched": matched,
                "trace": rendered_trace,
                "reasons": reasons,
                "topic_ids": topic_ids,
                "topic_labels": topic_labels,
            }
        )
        if trace.get("kind") == "ERROR":
            base_result["error"] = trace.get("reason")
        return base_result

    def match_rule(
        self,
        rule: Dict[str, Any],
        message: Dict[str, Any],
        *,
        trace_level: Optional[str] = None,
        debug_eval: bool = False,
    ) -> Dict[str, Any]:
        effective_trace_level = trace_level or self.default_trace_level
        if effective_trace_level not in TRACE_LEVELS:
            raise ValueError(f"trace_level 非法: {effective_trace_level}")

        payload = normalize_engine_output(message)
        compiled_rule = compile_rule(rule, regex_cache=self.regex_cache)
        return self._match_compiled_rule_with_payload(
            compiled_rule,
            payload,
            trace_level=effective_trace_level,
            short_circuit=not debug_eval,
        )

    def tag_message(
        self,
        message: Dict[str, Any],
        include_non_matches: bool = False,
        *,
        trace_level: Optional[str] = None,
        debug_eval: bool = False,
        stop_on_first_match: Optional[bool] = None,
    ) -> Dict[str, Any]:
        effective_trace_level = trace_level or self.default_trace_level
        if effective_trace_level not in TRACE_LEVELS:
            raise ValueError(f"trace_level 非法: {effective_trace_level}")

        payload = normalize_engine_output(message)
        matched_rules: List[Dict[str, Any]] = []
        unmatched_rules: List[Dict[str, Any]] = []
        topic_ids: List[str] = []
        topic_labels: List[str] = []

        should_stop_on_first = self.stop_on_first_match if stop_on_first_match is None else stop_on_first_match

        for compiled_rule in self.compiled_rules:
            result = self._match_compiled_rule_with_payload(
                compiled_rule,
                payload,
                trace_level=effective_trace_level,
                short_circuit=not debug_eval and self.short_circuit,
            )
            if result["matched"]:
                matched_rules.append(result)
                topic_ids.extend(result["topic_ids"])
                topic_labels.extend(result["topic_labels"])
                if should_stop_on_first:
                    break
            elif include_non_matches:
                unmatched_rules.append(result)

        return {
            "event": payload,
            "matched": bool(matched_rules),
            "topic_ids": uniq(topic_ids),
            "topic_labels": uniq(topic_labels),
            "matched_rules": matched_rules,
            "unmatched_rules": unmatched_rules if include_non_matches else [],
        }

    def tag_messages(
        self,
        messages: List[Dict[str, Any]],
        include_non_matches: bool = False,
        *,
        trace_level: Optional[str] = None,
        debug_eval: bool = False,
        stop_on_first_match: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        return [
            self.tag_message(
                message,
                include_non_matches=include_non_matches,
                trace_level=trace_level,
                debug_eval=debug_eval,
                stop_on_first_match=stop_on_first_match,
            )
            for message in safe_list(messages)
        ]


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
            },
            {
                "id": "rule_explicit_topic_01",
                "name": "显式赋值的高危泄露规则",
                "enabled": True,
                "status": "applied",
                "mode": "ast",
                "meta": {"owner": "SystemAdmin", "priority": 90, "desc": "高优先级规则"},
                "topic_id": "TopicDataLeak",
                "ast": {
                    "type": "GROUP",
                    "op": "AND",
                    "children": [
                        {"type": "COND", "field": "risk_score", "op": "gte", "value": "95"},
                        {"type": "COND", "field": "source_platform", "op": "eq", "value": "Forum"},
                    ],
                },
            },
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
            "severity": "CRITICAL",
            "risk_score": 99,
            "source_platform": "Forum",
            "labels": ["疑似售卖数据"],
            "raw_content": "打包出售某平台全量数据库。",
        },
    ]


def _cli() -> None:
    parser = argparse.ArgumentParser(description="支持编译层、优先级和分级 trace 的专题标签引擎")
    parser.add_argument("--rules", help="规则文件路径。支持导出配置对象{rules:[...]}或纯规则数组")
    parser.add_argument("--input", help="输入消息 JSON 文件路径。支持单条对象或对象数组")
    parser.add_argument("--include-non-matches", action="store_true", help="输出未命中规则详情")
    parser.add_argument("--validate", action="store_true", help="只校验规则，不执行打标")
    parser.add_argument("--write-example-rules", help="把示例规则写到指定路径")
    parser.add_argument("--write-example-input", help="把示例输入写到指定路径")
    parser.add_argument("--trace-level", choices=sorted(TRACE_LEVELS), default="summary", help="trace 输出级别，默认 summary")
    parser.add_argument("--debug-eval", action="store_true", help="调试模式：关闭短路，保留完整执行路径")
    parser.add_argument("--stop-on-first-match", action="store_true", help="按 priority 从高到低执行，命中首条规则后停止")
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

    engine = TopicRuleEngine.from_json_file(
        args.rules,
        default_trace_level=args.trace_level,
        short_circuit=not args.debug_eval,
        stop_on_first_match=args.stop_on_first_match,
    )

    if args.validate:
        print(json.dumps(engine.validate_rules(), ensure_ascii=False, indent=2))
        return

    if not args.input:
        parser.error("执行打标时必须提供 --input")

    raw_input = json.loads(Path(args.input).read_text(encoding="utf-8"))
    messages = raw_input if isinstance(raw_input, list) else [raw_input]
    result = engine.tag_messages(
        messages,
        include_non_matches=args.include_non_matches,
        trace_level=args.trace_level,
        debug_eval=args.debug_eval,
        stop_on_first_match=args.stop_on_first_match,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    _cli()