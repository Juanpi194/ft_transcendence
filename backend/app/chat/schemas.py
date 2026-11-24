"""
What the API receives and what it answers
"""

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints

from .constants import GROUP_NAME_MAX_LEN, GROUP_NAME_MIN_LEN, \
    MESSAGE_MAX_LEN, MESSAGE_MIN_LEN
from .domain import ConversationType, MemberRole


# Los espacios alrededor del texto se eliminan antes de comprobar su longitud.
GroupName = Annotated[str, StringConstraints(
    strip_whitespace=True,
    min_length=GROUP_NAME_MIN_LEN, max_length=GROUP_NAME_MAX_LEN)]
MessageText = Annotated[str, StringConstraints(
    strip_whitespace=True,
    min_length=MESSAGE_MIN_LEN, max_length=MESSAGE_MAX_LEN)]


# INPUT
class UserIdIn(BaseModel):
    user_id: int


class GroupIn(BaseModel):
    name: GroupName


class MessageIn(BaseModel):
    content: MessageText


# OUTPUT
class ConversationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    type: ConversationType
    name: str | None
    created_by: int
    created_at: datetime


class MemberOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    role: MemberRole
    joined_at: datetime


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    conversation_id: int
    sender_id: int
    content: str
    created_at: datetime


class BlockOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    blocked_id: int
    created_at: datetime
