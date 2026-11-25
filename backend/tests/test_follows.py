import pytest

from sqlalchemy.orm import Session

from app.services.follows import follow_user, unfollow_user, \
    accept_follow_request, reject_follow_request
from app.services.exceptions import SelfFollowError, UserNotFoundError, \
    AlreadyFollowingError, BlockedError, NotFollowingError, \
    FollowAlreadyAcceptedError, FollowRequestNotFoundError
from app.models import Follow
from app.core.constants import FOLLOW_ACCEPTED_TXT, FOLLOW_PENDING_TXT
from tests.helpers import create_user, create_block


def test_self_follow_error(db: Session) -> None:
    with pytest.raises(SelfFollowError):
        follow_user(db, 1, 1)


def test_follower_user_not_found_error(db: Session) -> None:
    unknown_user_id = -1000
    known_user = create_user(db, "known_user")
    with pytest.raises(UserNotFoundError):
        follow_user(db, unknown_user_id, known_user.id)


def test_followed_user_not_found_error(db: Session) -> None:
    known_user = create_user(db, "known_user")
    unknown_user_id = -1000
    with pytest.raises(UserNotFoundError):
        follow_user(db, known_user.id, unknown_user_id)


def test_follow_public_account(db: Session) -> None:
    user_1 = create_user(db, "user_1")
    user_2 = create_user(db, "user_2")
    follow = follow_user(db, user_1.id, user_2.id)
    assert follow.status == FOLLOW_ACCEPTED_TXT, \
        f"Follow status should be {FOLLOW_ACCEPTED_TXT} after following " \
        "a public account."
    assert db.get(Follow, (user_1.id, user_2.id)) is not None, \
        "The follow was not added to the database."


def test_follow_private_account(db: Session) -> None:
    user_1 = create_user(db, "user_1")
    private_user = create_user(db, "private_user", is_private=True)
    follow = follow_user(db, user_1.id, private_user.id)
    assert follow.status == FOLLOW_PENDING_TXT, \
        f"Follow status should be {FOLLOW_PENDING_TXT} after following " \
        "a private account."
    assert db.get(Follow, (user_1.id, private_user.id)) is not None, \
        "The follow was not added to the database."


def test_follow_each_other(db: Session) -> None:
    user_1 = create_user(db, "user_1")
    user_2 = create_user(db, "user_2")
    follow_user(db, user_1.id, user_2.id)
    follow_user(db, user_2.id, user_1.id)
    assert db.get(Follow, (user_1.id, user_2.id)) is not None, \
        f"The follow by {user_1.id} was not added to the database."
    assert db.get(Follow, (user_2.id, user_1.id)) is not None, \
        f"The follow by {user_2.id} was not added to the database."


def test_follow_already_following_error(db: Session) -> None:
    user_1 = create_user(db, "user_1")
    user_2 = create_user(db, "user_2")
    follow_user(db, user_1.id, user_2.id)
    with pytest.raises(AlreadyFollowingError):
        follow_user(db, user_1.id, user_2.id)


def test_follow_already_following_private_account_error(db: Session) -> None:
    user_1 = create_user(db, "user_1")
    private_user = create_user(db, "private_user", is_private=True)
    follow = follow_user(db, user_1.id, private_user.id)
    assert follow.status == FOLLOW_PENDING_TXT
    with pytest.raises(AlreadyFollowingError):
        follow_user(db, user_1.id, private_user.id)


def test_follow_blocked_user_error(db: Session) -> None:
    blocker = create_user(db, "user_1")
    blocked = create_user(db, "user_2")
    create_block(db, blocker, blocked)
    with pytest.raises(BlockedError):
        follow_user(db, blocker.id, blocked.id)


def test_follow_by_blocked_user_error(db: Session) -> None:
    blocker = create_user(db, "user_1")
    blocked = create_user(db, "user_2")
    create_block(db, blocker, blocked)
    with pytest.raises(BlockedError):
        follow_user(db, blocked.id, blocker.id)


def test_unfollow_followed_user(db: Session) -> None:
    follower = create_user(db, "follower")
    followed = create_user(db, "followed")
    follow_user(db, follower.id, followed.id)
    unfollow_user(db, follower.id, followed.id)
    assert db.get(Follow, (follower.id, followed.id)) is None, \
        "The follow still exists after the unfollow."


def test_unfollow_private_followed_user(db: Session) -> None:
    follower = create_user(db, "follower")
    private = create_user(db, "private", is_private=True)
    follow_user(db, follower.id, private.id)
    unfollow_user(db, follower.id, private.id)
    assert db.get(Follow, (follower.id, private.id)) is None, \
        "The follow still exists after the unfollow."


def test_unfollow_not_followed_user(db: Session) -> None:
    follower = create_user(db, "follower")
    not_followed = create_user(db, "not_followed")
    with pytest.raises(NotFollowingError):
        unfollow_user(db, follower.id, not_followed.id)


def test_unfollow_affects_only_one_direction(db: Session) -> None:
    user_1 = create_user(db, "user1")
    user_2 = create_user(db, "user2")
    follow_user(db, user_1.id, user_2.id)
    follow_user(db, user_2.id, user_1.id)
    unfollow_user(db, user_1.id, user_2.id)
    assert db.get(Follow, (user_1.id, user_2.id)) is None, \
        "The follow was not removed after unfollow."
    assert db.get(Follow, (user_2.id, user_1.id)) is not None, \
        "The follow was removed from both directions."


def test_accept_pending_request(db: Session) -> None:
    user = create_user(db, "user")
    private = create_user(db, "private", is_private=True)
    follow_user(db, user.id, private.id)
    follow = accept_follow_request(db, private.id, user.id)
    assert follow.status == FOLLOW_ACCEPTED_TXT, \
        "The follow request was not accepted."


def test_accept_already_accepted_request_error(db: Session) -> None:
    user = create_user(db, "user")
    private = create_user(db, "private", is_private=True)
    follow_user(db, user.id, private.id)
    accept_follow_request(db, private.id, user.id)
    with pytest.raises(FollowAlreadyAcceptedError):
        accept_follow_request(db, private.id, user.id)


def test_follow_request_not_found_error(db: Session) -> None:
    user = create_user(db, "user")
    private = create_user(db, "private", is_private=True)
    with pytest.raises(FollowRequestNotFoundError):
        accept_follow_request(db, private.id, user.id)


def test_reject_pending_request(db: Session) -> None:
    user = create_user(db, "user")
    private = create_user(db, "private", is_private=True)
    follow_user(db, user.id, private.id)
    reject_follow_request(db, private.id, user.id)
    follow = db.get(Follow, (user.id, private.id))
    assert follow is None, \
        "The rejection of the pending request was not done."


def test_reject_follow_request_not_found_error(db: Session) -> None:
    user = create_user(db, "user")
    private = create_user(db, "private", is_private=True)
    with pytest.raises(FollowRequestNotFoundError):
        reject_follow_request(db, private.id, user.id)


def test_reject_follow_already_accepted_error(db: Session) -> None:
    user = create_user(db, "user")
    private = create_user(db, "private", is_private=True)
    follow_user(db, user.id, private.id)
    accept_follow_request(db, private.id, user.id)
    with pytest.raises(FollowAlreadyAcceptedError):
        reject_follow_request(db, private.id, user.id)
    follow = db.get(Follow, (user.id, private.id))
    assert follow is not None, \
        "The already accepted follow should not be removed."
