"""
HTTP endpoints of the chat.

TODO: there are no rules yet (blocks, who can read, write or kick).
They will be in service.py, and these endpoints will call it.
"""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from .dependencies import CurrentUserId, Repository, check_user_exists
from .domain import Block, Conversation, Member, Message
from .repository import ChatRepository
from .schemas import BlockOut, ConversationOut, GroupIn, MemberOut, \
    MessageIn, MessageOut, UserIdIn


router = APIRouter(prefix="/chat", tags=["chat"])


def check_conversation_exists(repo: ChatRepository,
                              conversation_id: int) -> None:
    if repo.get_conversation(conversation_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            "Conversation not found")


# conversaciones
@router.get("/conversations", response_model=list[ConversationOut])
def list_my_conversations(me: CurrentUserId,
                          repo: Repository) -> list[Conversation]:
    return repo.list_conversations(me)


@router.post("/direct", response_model=ConversationOut)
def open_direct(body: UserIdIn, me: CurrentUserId,
                repo: Repository) -> Conversation:
    check_user_exists(body.user_id)
    return repo.get_or_create_direct(me, body.user_id)


@router.post("/groups", response_model=ConversationOut,
             status_code=status.HTTP_201_CREATED)
def create_group(body: GroupIn, me: CurrentUserId,
                 repo: Repository) -> Conversation:
    return repo.create_group(me, body.name)


# miembros
@router.get("/conversations/{conversation_id}/members",
            response_model=list[MemberOut])
def list_members(conversation_id: int, me: CurrentUserId,
                 repo: Repository) -> list[Member]:
    check_conversation_exists(repo, conversation_id)
    return repo.list_members(conversation_id)


@router.post("/conversations/{conversation_id}/members",
             response_model=MemberOut)
def add_member(conversation_id: int, body: UserIdIn, me: CurrentUserId,
               repo: Repository) -> Member:
    check_conversation_exists(repo, conversation_id)
    check_user_exists(body.user_id)
    return repo.add_member(conversation_id, body.user_id)


@router.delete("/conversations/{conversation_id}/members/{user_id}",
               status_code=status.HTTP_204_NO_CONTENT)
def remove_member(conversation_id: int, user_id: int, me: CurrentUserId,
                  repo: Repository) -> None:
    check_conversation_exists(repo, conversation_id)
    repo.remove_member(conversation_id, user_id)


# mensajes
@router.get("/conversations/{conversation_id}/messages",
            response_model=list[MessageOut])
def list_messages(conversation_id: int, me: CurrentUserId, repo: Repository,
                  limit: Annotated[int, Query(ge=1, le=100)] = 50,
                  before_id: int | None = None) -> list[Message]:
    check_conversation_exists(repo, conversation_id)
    return repo.list_messages(conversation_id, limit, before_id)


@router.post("/conversations/{conversation_id}/messages",
             response_model=MessageOut,
             status_code=status.HTTP_201_CREATED)
def send_message(conversation_id: int, body: MessageIn, me: CurrentUserId,
                 repo: Repository) -> Message:
    check_conversation_exists(repo, conversation_id)
    return repo.add_message(conversation_id, me, body.content)


# blockas
@router.get("/blocks", response_model=list[BlockOut])
def list_my_blocks(me: CurrentUserId, repo: Repository) -> list[Block]:
    return repo.list_blocks(me)


@router.put("/blocks/{user_id}", response_model=BlockOut)
def block_user(user_id: int, me: CurrentUserId, repo: Repository) -> Block:
    check_user_exists(user_id)
    return repo.add_block(me, user_id)


@router.delete("/blocks/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def unblock_user(user_id: int, me: CurrentUserId, repo: Repository) -> None:
    repo.remove_block(me, user_id)
