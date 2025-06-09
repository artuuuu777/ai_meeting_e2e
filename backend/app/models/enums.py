from enum import Enum


class MeetingStatus(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProcessingStatus(str, Enum):
    PENDING = "pending"
    TRANSCRIBING = "transcribing"
    EMBEDDING = "embedding"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"


class TemplateType(str, Enum):
    KEY_POINTS = "key_points"
    ACTION_ITEMS = "action_items"
    DECISIONS = "decisions"
    RISKS = "risks"
    BLOCKERS = "blockers"
    FOLLOW_UPS = "follow_ups"
    PARKING_LOT = "parking_lot"
    ROADMAP = "roadmap"
    KUDOS = "kudos"


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"


class ActionItemStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"