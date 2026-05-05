from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List, Union, Dict, Any, Callable, Literal
from datetime import datetime
import re

from app.schemas.enums import (
    SeverityLevel,
    ThreatCategory,
    RuleMode,
    RuleStatus,
    RbacScope,
    DedupeKey,
    ExcessAction,
    AstNodeType,
    AstGroupOp,
    AstCondOp,
    EnableStatus,
)


class CONDNode(BaseModel):
    type: Literal["COND"] = "COND"
    field: str
    op: AstCondOp
    value: Any


class GROUPNode(BaseModel):
    type: Literal["GROUP"] = "GROUP"
    op: AstGroupOp
    children: List[Union["GROUPNode", "CONDNode"]] = Field(default_factory=list)


GROUPNode.model_rebuild()


class BasicConfig(BaseModel):
    threat_category: List[str] = Field(default_factory=list)
    risk_level: Optional[SeverityLevel] = None
    risk_score: Optional[int] = None
    region: List[str] = Field(default_factory=list)
    entity_tags: List[str] = Field(default_factory=list)

    @field_validator("region", "entity_tags", "threat_category", mode="before")
    @classmethod
    def filter_empty_strings(cls, v):
        if isinstance(v, list):
            return [item for item in v if item != ""]
        return v


class ASTConfig(BaseModel):
    type: Optional[AstNodeType] = Field(default=None, validation_alias="type")
    op: Optional[AstGroupOp] = Field(default=None, validation_alias="op")
    children: Optional[List[Dict[str, Any]]] = Field(default=None, validation_alias="children")

    @model_validator(mode="before")
    @classmethod
    def handle_empty_dict(cls, values):
        if values is None:
            return {"type": None, "op": None, "children": None}
        if isinstance(values, dict) and not values:
            return {"type": None, "op": None, "children": None}
        return values

    def get_ast_root(self) -> Optional[Union[GROUPNode, CONDNode]]:
        if not self.type or not self.op:
            return None
        if self.type == AstNodeType.GROUP:
            return GROUPNode(op=self.op, children=self.children or [])
        elif self.type == AstNodeType.COND:
            if self.children and len(self.children) > 0:
                return CONDNode(**self.children[0])
            return None
        return None


class GovernanceConfig(BaseModel):
    dedupe_key: DedupeKey = DedupeKey.NONE
    dedupe_window: Optional[int] = 30
    frequency_hour: Optional[int] = 50
    excess: ExcessAction = ExcessAction.DROP


class DeliveryConfig(BaseModel):
    user_ids: List[str] = Field(default_factory=list)
    group_ids: List[str] = Field(default_factory=list)
    dashboard_enabled: EnableStatus = EnableStatus.ENABLED
    webhook_urls: List[str] = Field(default_factory=list)
    telegram_ids: List[str] = Field(default_factory=list)

    @field_validator("user_ids", "group_ids", "webhook_urls", "telegram_ids", mode="before")
    @classmethod
    def filter_empty_strings(cls, v):
        if isinstance(v, list):
            return [item for item in v if item != ""]
        return v


class MetaConfig(BaseModel):
    charge_person: Optional[str] = None
    priority: Optional[int] = 50
    summary: Optional[str] = None
    visible_scope: RbacScope = RbacScope.PRIVATE
    editor_ids: List[str] = Field(default_factory=list)

    @field_validator("editor_ids", mode="before")
    @classmethod
    def filter_empty_strings(cls, v):
        if isinstance(v, list):
            return [item for item in v if item != ""]
        return v


class SubscriptionTopicCreate(BaseModel):
    rule_name: str
    enabled: EnableStatus = EnableStatus.ENABLED
    status: RuleStatus = RuleStatus.DRAFT
    mode: RuleMode = RuleMode.BASIC

    basic_config: Optional[BasicConfig] = Field(default_factory=BasicConfig)
    ast_config: Optional[ASTConfig] = Field(default_factory=ASTConfig)
    governance: Optional[GovernanceConfig] = Field(default_factory=GovernanceConfig)
    delivery: Optional[DeliveryConfig] = Field(default_factory=DeliveryConfig)
    meta: Optional[MetaConfig] = Field(default_factory=MetaConfig)

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

        list_fields = ["region", "entity_tags", "user_ids", "group_ids", "webhook_urls", "telegram_ids", "editor_ids", "threat_category"]
        for field in list_fields:
            if field in values and isinstance(values[field], list):
                values[field] = [item for item in values[field] if item != ""]

        return values

    @model_validator(mode="after")
    def validate_rule_name_not_empty(self):
        if not self.rule_name or not self.rule_name.strip():
            raise ValueError("rule_name 字符串不能为空")
        return self

    @model_validator(mode="after")
    def validate_basic_mode(self):
        if not self.meta or not self.meta.charge_person:
            raise ValueError("meta.charge_person 字符串不能为空")
        return self


class SubscriptionTopicResponse(BaseModel):
    rule_code: str
    rule_name: Optional[str] = None
    enabled: EnableStatus = EnableStatus.ENABLED
    status: RuleStatus = RuleStatus.DRAFT
    mode: RuleMode = RuleMode.BASIC

    basic_config: Optional[BasicConfig] = Field(default_factory=BasicConfig)
    ast_config: Optional[ASTConfig] = Field(default_factory=ASTConfig)
    governance: Optional[GovernanceConfig] = Field(default_factory=GovernanceConfig)
    delivery: Optional[DeliveryConfig] = Field(default_factory=DeliveryConfig)
    meta: Optional[MetaConfig] = Field(default_factory=MetaConfig)

    created_at: datetime
    updated_at: datetime
    last_saved_draft_at: Optional[datetime] = None
    applied_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    final_syn_time: Optional[datetime] = None


class SubscriptionTopicListItem(BaseModel):
    rule_code: str
    rule_name: Optional[str] = None
    enabled: Optional[int] = 1
    status: Optional[str] = None
    charge_person: Optional[str] = None
    summary: Optional[str] = None
    final_syn_time: Optional[datetime] = None


class TopicIdNameItem(BaseModel):
    rule_code: str
    rule_name: Optional[str] = None


class RuleSaveRequest(BaseModel):
    rule_id: Optional[str] = Field(default=None, description="规则CODE，新增时为None或空字符串")
    rule_name: Optional[str] = Field(default=None, description="规则名称")
    enabled: EnableStatus = EnableStatus.ENABLED
    status: RuleStatus = RuleStatus.DRAFT
    mode: RuleMode = RuleMode.BASIC
    basic_config: Optional[Dict[str, Any]] = Field(default=None)
    ast_config: Optional[Dict[str, Any]] = Field(default=None)
    governance: Optional[Dict[str, Any]] = Field(default=None)
    delivery: Optional[Dict[str, Any]] = Field(default=None)
    meta: Optional[Dict[str, Any]] = Field(default=None)

    model_config = {"populate_by_name": True}


class HistoryRecordItem(BaseModel):
    history_id: str
    rule_code: str
    action: str
    operator: Optional[str] = None
    snapshot_data: Dict[str, Any]
    created_at: datetime


SubscriptionTopicPayload = SubscriptionTopicCreate


def _safe_get_field(payload: dict, field: str) -> tuple:
    try:
        keys = field.split(".")
        value = payload
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None, False
        return value, True
    except Exception:
        return None, False


def _eval_eq(payload_value: Any, rule_value: Any) -> bool:
    if payload_value is None:
        return False
    return str(payload_value) == str(rule_value)


def _eval_in_list(payload_value: Any, rule_value: str) -> bool:
    if payload_value is None:
        return False
    value_list = [v.strip() for v in str(rule_value).split(",") if v.strip()]
    return str(payload_value) in value_list


def _eval_not_in_list(payload_value: Any, rule_value: str) -> bool:
    return not _eval_in_list(payload_value, rule_value)


def _eval_contains(payload_value: Any, rule_value: str) -> bool:
    if payload_value is None:
        return False
    return str(rule_value) in str(payload_value)


def _eval_regex(payload_value: Any, rule_value: str) -> bool:
    if payload_value is None:
        return False
    try:
        return bool(re.search(str(rule_value), str(payload_value)))
    except re.error:
        return False


def _eval_numeric_compare(payload_value: Any, rule_value: str, op: str) -> bool:
    try:
        payload_num = float(payload_value)
        rule_num = float(rule_value)
        if op == "gt":
            return payload_num > rule_num
        elif op == "gte":
            return payload_num >= rule_num
        elif op == "lt":
            return payload_num < rule_num
        elif op == "lte":
            return payload_num <= rule_num
    except (TypeError, ValueError):
        pass
    return False


def _eval_exists(payload_value: Any) -> bool:
    return payload_value is not None and payload_value != ""


def _eval_not_exists(payload_value: Any) -> bool:
    return payload_value is None or payload_value == ""


COND_OPERATORS: Dict[str, Callable[[Any, Any], bool]] = {
    AstCondOp.EQ.value: _eval_eq,
    AstCondOp.IN_LIST.value: _eval_in_list,
    AstCondOp.NOT_IN_LIST.value: _eval_not_in_list,
    AstCondOp.CONTAINS.value: _eval_contains,
    AstCondOp.REGEX.value: _eval_regex,
    AstCondOp.GT.value: lambda p, r: _eval_numeric_compare(p, r, "gt"),
    AstCondOp.GTE.value: lambda p, r: _eval_numeric_compare(p, r, "gte"),
    AstCondOp.LT.value: lambda p, r: _eval_numeric_compare(p, r, "lt"),
    AstCondOp.LTE.value: lambda p, r: _eval_numeric_compare(p, r, "lte"),
    AstCondOp.EXISTS.value: lambda p, r: _eval_exists(p),
    AstCondOp.NOT_EXISTS.value: lambda p, r: _eval_not_exists(p),
}


def _evaluate_cond(node: CONDNode, payload: dict) -> bool:
    try:
        payload_value, field_exists = _safe_get_field(payload, node.field)
        if not field_exists:
            return False

        op_handler = COND_OPERATORS.get(node.op.value)
        if not op_handler:
            return False

        if node.op in (AstCondOp.EXISTS, AstCondOp.NOT_EXISTS):
            return op_handler(payload_value, None)
        return op_handler(payload_value, node.value)
    except Exception:
        return False


def _evaluate_group(node: GROUPNode, payload: dict) -> bool:
    try:
        children = node.children
        if not children:
            return False

        if node.op == AstGroupOp.AND:
            return all(_evaluate_ast(child, payload) for child in children)
        elif node.op == AstGroupOp.OR:
            return any(_evaluate_ast(child, payload) for child in children)
        elif node.op == AstGroupOp.NOT:
            if len(children) == 1:
                return not _evaluate_ast(children[0], payload)
            return False
        return False
    except Exception:
        return False


def _evaluate_ast(node: Union[GROUPNode, CONDNode], payload: dict) -> bool:
    try:
        if isinstance(node, GROUPNode):
            return _evaluate_group(node, payload)
        elif isinstance(node, CONDNode):
            return _evaluate_cond(node, payload)
        return False
    except Exception:
        return False


def evaluate_ast(ast_config: Optional[Union[ASTConfig, dict]], payload: dict) -> bool:
    try:
        if ast_config is None:
            return False

        if isinstance(ast_config, dict):
            ast_root_dict = ast_config
        elif isinstance(ast_config, ASTConfig):
            ast_root_dict = ast_config.model_dump() if hasattr(ast_config, 'model_dump') else ast_config
        else:
            return False

        if not ast_root_dict or not ast_root_dict.get("type"):
            return False

        node_type = ast_root_dict.get("type")
        if node_type == AstNodeType.GROUP.value:
            root_node = _parse_group_node(ast_root_dict)
            return _evaluate_ast(root_node, payload) if root_node else False
        elif node_type == AstNodeType.COND.value:
            root_node = _parse_cond_node(ast_root_dict)
            return _evaluate_ast(root_node, payload) if root_node else False
        return False
    except Exception:
        return False


def _parse_cond_node(node_dict: dict) -> Optional[CONDNode]:
    try:
        return CONDNode(
            type=AstNodeType.COND,
            field=node_dict.get("field", ""),
            op=AstCondOp(node_dict.get("op", "")),
            value=node_dict.get("value")
        )
    except Exception:
        return None


def _parse_group_node(node_dict: dict) -> Optional[GROUPNode]:
    try:
        children_list = []
        for child in node_dict.get("children", []):
            if child.get("type") == AstNodeType.GROUP.value:
                parsed_child = _parse_group_node(child)
                if parsed_child:
                    children_list.append(parsed_child)
            elif child.get("type") == AstNodeType.COND.value:
                parsed_child = _parse_cond_node(child)
                if parsed_child:
                    children_list.append(parsed_child)

        return GROUPNode(
            type=AstNodeType.GROUP,
            op=AstGroupOp(node_dict.get("op", "AND")),
            children=children_list
        )
    except Exception:
        return None


def check_topic_match(topic_config: dict, payload: dict) -> bool:
    mode = topic_config.get("mode", "basic")

    if mode == "ast":
        ast_conf = topic_config.get("ast_config")
        if not ast_conf:
            return False
        return evaluate_ast(ast_conf, payload)
    elif mode == "basic":
        basic_conf = topic_config.get("basic_config", {})
        threat_categories = basic_conf.get("threat_category", [])
        if not threat_categories:
            return False

        payload_threat = payload.get("threat_category", "")
        if not any(tc in payload_threat for tc in threat_categories):
            return False

        risk_level = basic_conf.get("risk_level")
        if risk_level:
            payload_risk = payload.get("risk_level", "")
            if payload_risk != risk_level:
                return False

        risk_score = basic_conf.get("risk_score", 0)
        if risk_score and payload.get("risk_score", 0) < risk_score:
            return False

        return True

    return False