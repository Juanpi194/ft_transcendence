from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models import User, Follow
from app.core.constants import FOLLOW_ACCEPTED_TXT
from app.services.exceptions import UserNotFoundError


def get_friends(db: Session, user_id: int) -> list[int]:
    if db.get(User, user_id) is None:
        raise UserNotFoundError(f"User '{user_id}' does not exist.")

    # Storing the *statement* in a variable.
    stmt_user_following = select(Follow.followed_id).where(
        (Follow.follower_id == user_id) &
        (Follow.status == FOLLOW_ACCEPTED_TXT)
        )

    # Rows where the user is the follower, and selected the followed_id column.
    user_follows_rows = db.execute(stmt_user_following).all()

    # Storing the *statement* in a variable.
    stmt_user_followers = select(Follow.follower_id).where(
        (Follow.followed_id == user_id) &
        (Follow.status == FOLLOW_ACCEPTED_TXT)
    )

    # Rows where the user is the followed, and selected the follower_id column.
    user_followers_rows = db.execute(stmt_user_followers).all()

    # Do the intersection
    follows_ids = [follow[0] for follow in user_follows_rows]
    followers_ids = [follower[0] for follower in user_followers_rows]
    follow_intersection: set[int] = set(follows_ids) & set(followers_ids)
    return list(follow_intersection)
