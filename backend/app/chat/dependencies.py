"""
What the endpoints need from the rest of the project.

Everything here is TEMPORARY: when the login and the database are ready,
this is the file that has to change.
"""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from .memory import MemoryChatRepository
from .repository import ChatRepository


FAKE_USERS = {1: "ana", 2: "luis", 3: "eva"}

_repository = MemoryChatRepository()
_user_id_header = APIKeyHeader(name="X-User-Id",
                               description="1 = ana, 2 = luis, 3 = eva")


def get_repository() -> ChatRepository:
    return _repository


def get_current_user_id(
        header: Annotated[str, Depends(_user_id_header)]) -> int:
    """
    Fake login: it believes whoever the header says you are.
    Never use it in the real app.
    """
    for user_id in FAKE_USERS:
        if header == str(user_id):
            return user_id
    raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unknown user")


def check_user_exists(user_id: int) -> None:
    if user_id not in FAKE_USERS:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")


Repository = Annotated[ChatRepository, Depends(get_repository)]
CurrentUserId = Annotated[int, Depends(get_current_user_id)]
