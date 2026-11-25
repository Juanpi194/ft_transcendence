import pytest

from sqlalchemy.orm import Session

from app.services.follows import follow_user
from app.services.friends import get_friends
from app.services.exceptions import UserNotFoundError
from tests.helpers import create_user


def test_get_friends(db: Session) -> None:
    user_1 = create_user(db, "user_1")
    user_2 = create_user(db, "user_2")
    user_3 = create_user(db, "user_3")
    follow_user(db, user_1.id, user_2.id)
    follow_user(db, user_1.id, user_3.id)
    follow_user(db, user_3.id, user_1.id)
    user_1_friends = get_friends(db, user_1.id)
    assert len(user_1_friends) == 1, \
        f"User '{user_1.id}' friend list should only contain '{user_3.id}'."
    assert user_1_friends[0] == user_3.id, \
        f"User '{user_3.id}' was not added to '{user_1.id}' friend list."


def test_get_friends_empty(db: Session) -> None:
    user = create_user(db, "user")
    user_friends = get_friends(db, user.id)
    assert len(user_friends) == 0, \
        f"User '{user.id}' friend list should be empty."


def test_pending_request_is_not_friend(db: Session) -> None:
    private_user = create_user(db, "private_user", is_private=True)
    public_user = create_user(db, "public_user")
    follow_user(db, private_user.id, public_user.id)
    follow_user(db, public_user.id, private_user.id)
    private_user_friends = get_friends(db, private_user.id)
    assert len(private_user_friends) == 0, \
        f"'{private_user.id}' should not be friend of '{public_user.id}'."
    public_user_friends = get_friends(db, public_user.id)
    assert len(public_user_friends) == 0, \
        f"'{public_user.id}' should not be friend of '{private_user.id}'."


def test_user_not_found(db: Session) -> None:
    unknown_user_id = -1000
    with pytest.raises(UserNotFoundError):
        get_friends(db, unknown_user_id)
