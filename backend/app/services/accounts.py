from sqlalchemy.orm import Session
from sqlalchemy import update

from ..models import User, Follow
from .exceptions import UserNotFoundError, AccountAlreadyPrivateError, \
    AccountAlreadyPublicError
from ..core.constants import FOLLOW_PENDING_TXT, FOLLOW_ACCEPTED_TXT


def make_account_private(db: Session, user_id: int) -> None:
    user = db.get(User, user_id)
    if user is None:
        raise UserNotFoundError(f"User {user_id} does not exist.")
    if user.is_private:
        raise AccountAlreadyPrivateError(f"User {user_id} is already "
                                         "a private account.")
    user.is_private = True
    db.commit()


def make_account_public(db: Session, user_id: int) -> None:
    user = db.get(User, user_id)
    if user is None:
        raise UserNotFoundError(f"User {user_id} does not exist.")
    if not user.is_private:
        raise AccountAlreadyPublicError(f"User {user_id} is already "
                                        "a public account.")
    user.is_private = False
    db.execute(update(Follow).where(
        Follow.followed_id == user_id,
        Follow.status == FOLLOW_PENDING_TXT
        ).values(status=FOLLOW_ACCEPTED_TXT))
    db.commit()
