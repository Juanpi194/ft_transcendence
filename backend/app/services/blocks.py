from sqlalchemy.orm import Session
from sqlalchemy import delete

from ..models import Block, User, Follow
from .exceptions import UserNotFoundError, SelfBlockError, AlreadyBlockedError


def block_user(db: Session, blocker_id: int, blocked_id: int) -> Block:
    if blocker_id == blocked_id:
        raise SelfBlockError(f"User '{blocker_id}' tried to self-block.")
    blocker = db.get(User, blocker_id)
    if blocker is None:
        raise UserNotFoundError(f"User '{blocker_id}' not found.")
    blocked = db.get(User, blocked_id)
    if blocked is None:
        raise UserNotFoundError(f"User '{blocked_id}' not found.")
    block = db.get(Block, (blocker_id, blocked_id))
    if block is not None:
        raise AlreadyBlockedError(f"User '{blocker_id}' already blocked "
                                  f"user '{blocked_id}'.")

    # At this point the block is acceptable
    block = Block(blocker_id=blocker_id, blocked_id=blocked_id)
    db.execute(delete(Follow).where(
        ((Follow.follower_id == blocker_id) &
         (Follow.followed_id == blocked_id)) |
        ((Follow.follower_id == blocked_id) &
         (Follow.followed_id == blocker_id))
    ))
    db.add(block)
    db.commit()
    db.refresh(block)
    return block
