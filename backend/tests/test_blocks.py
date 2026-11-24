import pytest

from sqlalchemy.orm import Session

from app.services.follows import follow_user
from app.services.blocks import block_user
from app.services.exceptions import SelfBlockError, UserNotFoundError, \
    AlreadyBlockedError
from app.models import Follow
from tests.helpers import create_user


def test_block_user(db: Session) -> None:
    user_1 = create_user(db, "user_1")
    user_2 = create_user(db, "user_2")
    block = block_user(db, user_1.id, user_2.id)
    assert block is not None, \
        "The block was not created."
    assert block.blocker_id == user_1.id, \
        "The block does not have the right blocker id."
    assert block.blocked_id == user_2.id, \
        "The block does not have the right blocked id."


def test_autoblock_error(db: Session) -> None:
    user = create_user(db, "user")
    with pytest.raises(SelfBlockError):
        block_user(db, user.id, user.id)


def test_user_that_blocks_not_found(db: Session) -> None:
    unknown_user_id = -1000
    user = create_user(db, "user")
    with pytest.raises(UserNotFoundError):
        block_user(db, unknown_user_id, user.id)


def test_block_user_not_found_error(db: Session) -> None:
    user = create_user(db, "user")
    unknown_user_id = -1000
    with pytest.raises(UserNotFoundError):
        block_user(db, user.id, unknown_user_id)


def test_block_follower(db: Session) -> None:
    user_1 = create_user(db, "user_1")
    user_2 = create_user(db, "user_2")
    follow_user(db, user_2.id, user_1.id)
    block_user(db, user_1.id, user_2.id)
    follow = db.get(Follow, (user_2.id, user_1.id))
    assert follow is None, \
        "The follow was not removed."


def test_block_followed_follower(db: Session) -> None:
    user_1 = create_user(db, "user_1")
    user_2 = create_user(db, "user_2")
    follow_user(db, user_1.id, user_2.id)
    follow_user(db, user_2.id, user_1.id)
    block_user(db, user_1.id, user_2.id)
    follow_1_2 = db.get(Follow, (user_1.id, user_2.id))
    follow_2_1 = db.get(Follow, (user_2.id, user_1.id))
    assert follow_1_2 is None, \
        f"The follow from '{user_1.id}' should have been deleted."
    assert follow_2_1 is None, \
        f"The follow from '{user_2.id}' should have been deleted."


def test_block_only_removes_follows_between_both_users(db: Session) -> None:
    user_1 = create_user(db, "user1")
    user_2 = create_user(db, "user2")
    user_3 = create_user(db, "user3")
    follow_user(db, user_1.id, user_2.id)
    follow_user(db, user_1.id, user_3.id)
    follow_user(db, user_2.id, user_1.id)
    follow_user(db, user_2.id, user_3.id)
    follow_user(db, user_3.id, user_1.id)
    follow_user(db, user_3.id, user_2.id)
    block_user(db, user_1.id, user_2.id)
    for pair in [(user_1.id, user_2.id), (user_2.id, user_1.id)]:
        assert db.get(Follow, pair) is None, \
            f"The follow between '{pair[0]}' and '{pair[1]}' should not exist."
    for pair in [(user_1.id, user_3.id), (user_3.id, user_1.id),
                 (user_2.id, user_3.id), (user_3.id, user_2.id)]:
        assert db.get(Follow, pair) is not None, \
            f"The follow between '{pair[0]}' and '{pair[1]}' should exist."


def test_already_blocked_error(db: Session) -> None:
    user_1 = create_user(db, "user_1")
    user_2 = create_user(db, "user_2")
    block_user(db, user_1.id, user_2.id)
    with pytest.raises(AlreadyBlockedError):
        block_user(db, user_1.id, user_2.id)
