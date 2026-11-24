"""
What the chat needs to store, without saying how.

Any class with these methods can be used as a repository: the one in
memory (memory.py) for now, one with SQLAlchemy later.
A repository only stores and reads data, the rules live in the service.
"""

from typing import Protocol

from .domain import Block, Conversation, Member, MemberRole, Message


class ChatRepository(Protocol):
    # conversaciones
    def get_or_create_direct(self, user_id: int,
                             other_id: int) -> Conversation:
        """Return the private chat of both users, it is never duplicated."""
        ...

    def create_group(self, owner_id: int, name: str) -> Conversation:
        """Create a group with its owner already inside."""
        ...

    def get_conversation(self, conversation_id: int) -> Conversation | None:
        ...

    def list_conversations(self, user_id: int) -> list[Conversation]:
        """Every conversation the user is a member of."""
        ...

    # mimrbos
    def add_member(self, conversation_id: int, user_id: int) -> Member:
        """If the user is already a member, nothing changes."""
        ...

    def get_member(self, conversation_id: int,
                   user_id: int) -> Member | None:
        ...

    def list_members(self, conversation_id: int) -> list[Member]:
        """From the oldest member to the newest."""
        ...

    def remove_member(self, conversation_id: int, user_id: int) -> None:
        ...

    def set_role(self, conversation_id: int, user_id: int,
                 role: MemberRole) -> None:
        ...

    def set_last_read(self, conversation_id: int, user_id: int,
                      message_id: int) -> None:
        ...

    # mensajes
    def add_message(self, conversation_id: int, sender_id: int,
                    content: str) -> Message:
        ...

    def list_messages(self, conversation_id: int, limit: int,
                      before_id: int | None = None) -> list[Message]:
        """
        The last messages, from the oldest to the newest.
        With before_id, only the ones previous to that message.
        """
        ...

    # blocks
    def add_block(self, blocker_id: int, blocked_id: int) -> Block:
        """If the block already exists, nothing changes."""
        ...

    def remove_block(self, blocker_id: int, blocked_id: int) -> None:
        ...

    def is_blocked(self, blocker_id: int, blocked_id: int) -> bool:
        """Only checks one direction: blocker_id blocked blocked_id."""
        ...

    def list_blocks(self, blocker_id: int) -> list[Block]:
        """Every block made by the user."""
        ...
