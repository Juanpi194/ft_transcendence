"""
Plain data used by the chat.

Nothing here knows about the database or FastAPI.
Users are only referenced by their id (users.id is an integer).
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ConversationType(str, Enum):
    DIRECT = "direct"
    GROUP = "group"


class MemberRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


@dataclass
class Conversation:
    """A private chat (two members) or a group."""
    id: int
    type: ConversationType
    created_by: int
    created_at: datetime
    name: str | None = None
    """Only groups have a name."""


@dataclass
class Member:
    """A user inside a conversation."""
    conversation_id: int
    user_id: int
    joined_at: datetime
    role: MemberRole = MemberRole.MEMBER
    last_read_message_id: int | None = None


@dataclass(frozen=True)
class Message:
    id: int
    conversation_id: int
    sender_id: int
    content: str
    created_at: datetime


@dataclass(frozen=True)
class Block:
    """blocker_id does not want to hear from blocked_id."""
    blocker_id: int
    blocked_id: int
    created_at: datetime
