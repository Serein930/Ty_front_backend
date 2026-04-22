from enum import Enum, IntEnum


class EnableStatus(IntEnum):
    DISABLED = 0
    ENABLED = 1


class BooleanFlag(IntEnum):
    FALSE = 0
    TRUE = 1


class SeverityLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ThreatCategory(str, Enum):
    DRUGS = "TopicDrugs"
    SMUGGLE = "TopicSmuggle"
    TERROR = "TopicTerror"
    DATA_LEAK = "TopicDataLeak"
    CYBERCRIME = "TopicCybercrime"
    APT = "TopicAPT"
    TAIWAN = "TopicTaiwan"
    RANSOM = "TopicRansom"
    UNKNOWN = "UNKNOWN"


class PlatformType(str, Enum):
    TELEGRAM = "Telegram"
    TOR = "Tor"
    WEIBO = "Weibo"
    I2P = "I2P"
    X = "X"
    FORUM = "Forum"
    DARKWEB = "DarkWeb"
    NEWS = "News"
    UNKNOWN = "UNKNOWN"


class RbacScope(str, Enum):
    PRIVATE = "private"
    TEAM = "team"
    ORG = "org"


class RuleStatus(str, Enum):
    DRAFT = "draft"
    APPLIED = "applied"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class RuleMode(str, Enum):
    BASIC = "basic"
    AST = "ast"


class DedupeKey(str, Enum):
    NONE = "none"
    CONTENT_HASH = "content_hash"
    ENTITY = "entity"
    SOURCE_HANDLE = "source_handle"


class ExcessAction(str, Enum):
    DROP = "drop"
    DIGEST = "digest"
    DOWNGRADE = "downgrade"


class AstNodeType(str, Enum):
    GROUP = "GROUP"
    COND = "COND"


class AstGroupOp(str, Enum):
    AND = "AND"
    OR = "OR"
    NOT = "NOT"


class AstCondOp(str, Enum):
    EQ = "eq"
    IN_LIST = "in_list"
    NOT_IN_LIST = "not_in_list"
    CONTAINS = "contains"
    REGEX = "regex"
    GT = "gt"
    GTE = "gte"
    LT = "lt"
    LTE = "lte"
    RANGE = "range"
    EXISTS = "exists"
    NOT_EXISTS = "not_exists"
    IS_TRUE = "is_true"
    IS_FALSE = "is_false"
    ANY_OF = "any_of"
    ALL_OF = "all_of"
    NONE_OF = "none_of"


class DispositionStatus(str, Enum):
    OPEN = "open"
    ASSIGNED = "assigned"
    CONFIRMED = "confirmed"
    CLOSED = "closed"
    CASE = "case"
    CLUE = "clue"
    IGNORED = "ignored"


class CaseStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    CLOSED = "closed"


class ClueStatus(str, Enum):
    NEW = "new"
    PROCESSING = "processing"
    ARCHIVED = "archived"


class ReviewState(str, Enum):
    UNREVIEWED = "unreviewed"
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    MODIFIED = "modified"
    CLOSED = "closed"


class PatchType(str, Enum):
    MANUAL_PATCH = "manual_patch"
    ALIAS_MERGE = "alias_merge"
    EVIDENCE_ACCEPT = "evidence_accept"
    EVIDENCE_REJECT = "evidence_reject"
    TAG_EDIT = "tag_edit"


class RelationLabel(str, Enum):
    SELF = "self"
    DUPLICATE = "duplicate"
    RELATED = "related"
    WEAK_RELATED = "weak_related"
    NOT_RELATED = "not_related"


class MergeDecision(str, Enum):
    PENDING = "pending"
    MERGE = "merge"
    REJECT_MERGE = "reject_merge"
    NEED_MORE_EVIDENCE = "need_more_evidence"