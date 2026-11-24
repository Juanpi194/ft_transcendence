from sqlalchemy.orm import Session

from ..models import User, Block, Follow
from .exceptions import SelfFollowError, UserNotFoundError, \
    BlockedError, AlreadyFollowingError, NotFollowingError, \
    FollowAlreadyAcceptedError, FollowRequestNotFoundError
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


def unfollow_user(db: Session, follower_id: int, followed_id: int) -> None:
    follow = db.get(Follow, (follower_id, followed_id))
    if follow is None:
        raise NotFollowingError(f"User '{follower_id}' "
                                f"does not follow user '{followed_id}'.")
    db.delete(follow)
    db.commit()


def accept_follow_request(db: Session,
                          user_id: int, requester_id: int) -> Follow:
    """
    user_id is the one that decides to accept or reject the request,
    requester_id is the one that requested the follow.
    """
    follow = db.get(Follow, (requester_id, user_id))
    if follow is None:
        raise FollowRequestNotFoundError(f"User '{requester_id}' has not "
                                         f"requested to follow '{user_id}'.")
    if follow.status == FOLLOW_ACCEPTED_TXT:
        raise FollowAlreadyAcceptedError(f"User '{user_id}' already "
                                         f"accepted '{requester_id}' request.")
    follow.status = FOLLOW_ACCEPTED_TXT
    db.commit()
    return follow


def reject_follow_request(db: Session,
                          user_id: int, requester_id: int) -> None:
    """
    user_id is the one that decides to accept or reject the request,
    requester_id is the one that requested the follow.
    """
    follow = db.get(Follow, (requester_id, user_id))
    if follow is None:
        raise FollowRequestNotFoundError(f"User '{requester_id}' has not "
                                         f"requested to follow '{user_id}'.")
    if follow.status == FOLLOW_ACCEPTED_TXT:
        raise FollowAlreadyAcceptedError(f"User '{user_id}' already "
                                         f"accepted '{requester_id}' request.")
    db.delete(follow)
    db.commit()
