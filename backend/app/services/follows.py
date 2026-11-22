from sqlalchemy.orm import Session

from ..models import User, Block, Follow
from .exceptions import SelfFollowError, UserNotFoundError, \
    BlockedError, AlreadyFollowingError
from ..core.constants import FOLLOW_PENDING_TXT, FOLLOW_ACCEPTED_TXT


def follow_user(db: Session, follower_id: int, followed_id: int) -> Follow:
    if follower_id == followed_id:
        raise SelfFollowError(f"User '{follower_id}' "
                              "tried to self-follow")
    follower = db.get(User, follower_id)
    if follower is None:
        raise UserNotFoundError(f"User '{follower_id}' does not exist")
    followed = db.get(User, followed_id)
    if followed is None:
        raise UserNotFoundError(f"User '{followed_id}' does not exist")
    follower_blocked_followed = db.get(Block, (follower_id, followed_id))
    if follower_blocked_followed is not None:
        raise BlockedError(f"User '{follower_id}' blocked '{followed_id}'")
    followed_blocked_follower = db.get(Block, (followed_id, follower_id))
    if followed_blocked_follower is not None:
        raise BlockedError(f"User '{followed_id}' blocked '{follower_id}'")
    follower_follows_followed = db.get(Follow, (follower_id, followed_id))
    if follower_follows_followed is not None:
        raise AlreadyFollowingError(f"User '{follower_id}' already "
                                    f"follows '{followed_id}'")

    # At this point the follow is acceptable
    status = FOLLOW_PENDING_TXT if followed.is_private else FOLLOW_ACCEPTED_TXT
    follow = Follow(follower_id=follower_id, followed_id=followed_id,
                    status=status)
    db.add(follow)
    db.commit()
    db.refresh(follow)
    return follow
