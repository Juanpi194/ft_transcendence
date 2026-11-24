"""
Temporary storage with dictionaries. Everything is lost when the server stops.
"""

from dataclasses import replace
from datetime import datetime, timezone
from itertools import count
from threading import RLock

from .domain import Block, Conversation, ConversationType, Member, \
    MemberRole, Message


def _now() -> datetime:
    return datetime.now(timezone.utc)


class MemoryChatRepository:
    """
    Implements ChatRepository.

    FastAPI may run several requests at the same time in different threads,
    so every method that touches the data takes the lock first.
    Conversations and members are returned as copies: changing one of them
    does not change what is stored, just like with a real database.
    """

    def __init__(self) -> None:
        self._lock = RLock()
        self._conversation_ids = count(1)
        self._message_ids = count(1)
        self._conversations: dict[int, Conversation] = {}
        self._direct_ids: dict[tuple[int, int], int] = {}
        """(lower user id, higher user id) -> conversation id"""
        self._members: dict[int, dict[int, Member]] = {}
        """conversation id -> user id -> member"""
        self._messages: dict[int, list[Message]] = {}
        """conversation id -> messages"""
        self._blocks: dict[tuple[int, int], Block] = {}
        """(blocker id, blocked id) -> block"""

    # conversacioones
    def get_or_create_direct(self, user_id: int,
                             other_id: int) -> Conversation:
        key = (min(user_id, other_id), max(user_id, other_id))
        with self._lock:
            if key not in self._direct_ids:
                conversation = self._create(ConversationType.DIRECT, user_id)
                self._add_member(conversation.id, user_id, MemberRole.MEMBER)
                self._add_member(conversation.id, other_id, MemberRole.MEMBER)
                self._direct_ids[key] = conversation.id
            return replace(self._conversations[self._direct_ids[key]])

    def create_group(self, owner_id: int, name: str) -> Conversation:
        with self._lock:
            conversation = self._create(ConversationType.GROUP, owner_id,
                                        name)
            self._add_member(conversation.id, owner_id, MemberRole.OWNER)
            return replace(conversation)

    def get_conversation(self, conversation_id: int) -> Conversation | None:
        with self._lock:
            conversation = self._conversations.get(conversation_id)
            return replace(conversation) if conversation else None

    def list_conversations(self, user_id: int) -> list[Conversation]:
        with self._lock:
            return [replace(conversation)
                    for conversation in self._conversations.values()
                    if user_id in self._members[conversation.id]]

    # usuarios
    def add_member(self, conversation_id: int, user_id: int) -> Member:
        with self._lock:
            members = self._members[conversation_id]
            if user_id not in members:
                self._add_member(conversation_id, user_id, MemberRole.MEMBER)
            return replace(members[user_id])

    def get_member(self, conversation_id: int,
                   user_id: int) -> Member | None:
        with self._lock:
            member = self._members.get(conversation_id, {}).get(user_id)
            return replace(member) if member else None

    def list_members(self, conversation_id: int) -> list[Member]:
        with self._lock:
            members = self._members.get(conversation_id, {})
            return [replace(member) for member in members.values()]

    def remove_member(self, conversation_id: int, user_id: int) -> None:
        with self._lock:
            self._members.get(conversation_id, {}).pop(user_id, None)

    def set_role(self, conversation_id: int, user_id: int,
                 role: MemberRole) -> None:
        with self._lock:
            self._members[conversation_id][user_id].role = role

    def set_last_read(self, conversation_id: int, user_id: int,
                      message_id: int) -> None:
        with self._lock:
            member = self._members[conversation_id][user_id]
            member.last_read_message_id = message_id

    # mensajes
    def add_message(self, conversation_id: int, sender_id: int,
                    content: str) -> Message:
        with self._lock:
            messages = self._messages[conversation_id]
            message = Message(id=next(self._message_ids),
                              conversation_id=conversation_id,
                              sender_id=sender_id,
                              content=content,
                              created_at=_now())
            messages.append(message)
            return message

    def list_messages(self, conversation_id: int, limit: int,
                      before_id: int | None = None) -> list[Message]:
        if limit <= 0:
            return []
        with self._lock:
            messages = self._messages.get(conversation_id, [])
            if before_id is not None:
                messages = [m for m in messages if m.id < before_id]
            return messages[-limit:]

    # blocks
    def add_block(self, blocker_id: int, blocked_id: int) -> Block:
        key = (blocker_id, blocked_id)
        with self._lock:
            if key not in self._blocks:
                self._blocks[key] = Block(blocker_id, blocked_id, _now())
            return self._blocks[key]

    def remove_block(self, blocker_id: int, blocked_id: int) -> None:
        with self._lock:
            self._blocks.pop((blocker_id, blocked_id), None)

    def is_blocked(self, blocker_id: int, blocked_id: int) -> bool:
        with self._lock:
            return (blocker_id, blocked_id) in self._blocks

    def list_blocks(self, blocker_id: int) -> list[Block]:
        with self._lock:
            return [block for block in self._blocks.values()
                    if block.blocker_id == blocker_id]

    # FUNCIONES AUXILIARES
    def _create(self, type_: ConversationType, created_by: int,
                name: str | None = None) -> Conversation:
        conversation = Conversation(id=next(self._conversation_ids),
                                    type=type_,
                                    created_by=created_by,
                                    created_at=_now(),
                                    name=name)
        self._conversations[conversation.id] = conversation
        self._members[conversation.id] = {}
        self._messages[conversation.id] = []
        return conversation

    def _add_member(self, conversation_id: int, user_id: int,
                    role: MemberRole) -> None:
        self._members[conversation_id][user_id] = Member(
            conversation_id=conversation_id, user_id=user_id,
            joined_at=_now(), role=role)
