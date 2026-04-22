from __future__ import annotations

import argparse
import json
import re
import time
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from topic_ast_engine import (
    APP,
    SEVERITY_ORDER,
    SCHEMA_TOPICS,
    TOPIC_NAME_MAP,
    FIELD_TYPE_MAP,
    TopicRuleEngine,
    normalize_rule,
    normalize_engine_output,
    eval_basic,
    eval_ast,
    flatten_trace_reasons,
    infer_topics_from_rule,
    safe_list,
    uniq,
    csv_to_list,
    canon,
    now_ms,
    new_trace_id,
    _to_number,
    _normalize_string_list,
    validate_rule,
    _default_basic,
    _default_ast,
    build_example_rules,
    build_example_messages,
)

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


def normalize_engine_output_extended(raw: Dict[str, Any]) -> Dict[str, Any]:
    r = deepcopy(raw) or {}
    original_entity_tags = r.get("entity_tags")

    if "entity_tags" in r:
        r["labels"] = r["entity_tags"]

    out = normalize_engine_output(r)

    if original_entity_tags is not None:
        out["entity_tags"] = original_entity_tags

    return out


def _convert_topics_json_to_rules(topics_json: Dict[str, Any]) -> List[Dict[str, Any]]:
    rules: List[Dict[str, Any]] = []

    def convert_ast_fields(node: Dict[str, Any]) -> None:
        if not isinstance(node, dict):
            return
        if node.get("field") == "entity_tags":
            node["field"] = "labels"
        if node.get("field") in ("labels", "ioc_location", "entity_tags") and node.get("op") == "contains":
            node["op"] = "any_of"
        for child in safe_list(node.get("children")):
            convert_ast_fields(child)

    for rule_id, rule_data in topics_json.items():
        if not rule_data or rule_data.get("deleted_at"):
            continue

        enabled = rule_data.get("enabled")
        if enabled in (1, "1", True, "true"):
            enabled = True
        elif enabled in (0, "0", False, "false"):
            enabled = False
        else:
            enabled = True

        mode = str(rule_data.get("mode") or "basic").lower()

        basic_cfg = rule_data.get("basic_config") or {}
        ast_cfg = rule_data.get("ast_config")

        normalized: Dict[str, Any] = {
            "id": str(rule_id),
            "name": rule_data.get("name") or "未命名规则",
            "enabled": enabled,
            "status": rule_data.get("status") or "draft",
            "mode": mode,
        }

        if mode == "basic":
            normalized["basic"] = {
                "topics": uniq([str(x).strip() for x in safe_list(basic_cfg.get("threat_category")) if str(x).strip()]),
                "severity": canon("severity", basic_cfg.get("risk_level") or "MEDIUM"),
                "risk_min": basic_cfg.get("risk_score"),
                "locations": uniq([canon("ioc_location", x) for x in safe_list(basic_cfg.get("region")) if str(x).strip()]),
                "labels": uniq([canon("labels", x) for x in safe_list(basic_cfg.get("entity_tags")) if str(x).strip()]),
            }
            normalized["ast"] = _default_ast()
        else:
            normalized["basic"] = _default_basic()
            if isinstance(ast_cfg, dict) and ast_cfg.get("type"):
                ast_copy = deepcopy(ast_cfg)
                convert_ast_fields(ast_copy)
                normalized["ast"] = ast_copy
            else:
                normalized["ast"] = _default_ast()

        meta = rule_data.get("meta") or {}
        normalized["meta"] = {
            "owner": meta.get("charge_person") or "",
            "priority": int(meta.get("priority") or 50),
            "desc": meta.get("summary") or "",
        }

        governance = rule_data.get("governance") or {}
        normalized["_governance"] = governance

        delivery = rule_data.get("delivery") or {}
        normalized["_delivery"] = delivery

        created_at = rule_data.get("created_at")
        updated_at = rule_data.get("updated_at")
        applied_at = rule_data.get("applied_at")
        normalized["_timestamps"] = {
            "created_at": created_at,
            "updated_at": updated_at,
            "applied_at": applied_at,
        }

        rules.append(normalized)

    return rules


class TopicsJsonRuleEngine:
    def __init__(self, rules: List[Dict[str, Any]]) -> None:
        self.rules: List[Dict[str, Any]] = [normalize_rule(rule) for rule in safe_list(rules)]

    @classmethod
    def from_json_file(cls, path: str | Path) -> "TopicsJsonRuleEngine":
        data = json.loads(Path(path).read_text(encoding="utf-8"))

        if isinstance(data, dict):
            if all(isinstance(v, dict) for v in data.values()) and any(
                k in v for v in data.values() for k in ("basic_config", "ast_config", "governance", "delivery")
            ):
                rules = _convert_topics_json_to_rules(data)
            elif isinstance(data.get("rules"), list):
                rules = data["rules"]
            elif isinstance(data, list):
                rules = data
            else:
                raise ValueError("文件格式不正确")
        elif isinstance(data, list):
            rules = data
        else:
            raise ValueError("文件格式不正确")

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
        payload = normalize_engine_output_extended(message)
        return self._match_rule_with_payload(normalize_rule(rule), payload)

    def tag_message(self, message: Dict[str, Any], include_non_matches: bool = False) -> Dict[str, Any]:
        payload = normalize_engine_output_extended(message)
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


def _cli() -> None:
    parser = argparse.ArgumentParser(description="专题标签引擎 - 支持原格式和 topics.json 格式")
    parser.add_argument("--rules", help="规则文件路径，支持原格式和 topics.json 格式")
    parser.add_argument("--input", help="输入消息 JSON 文件路径")
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
        parser.error("必须提供 --rules")

    engine = TopicsJsonRuleEngine.from_json_file(args.rules)

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
