import pytest

from sqlalchemy.orm import Session

from app.services.accounts import make_account_public, make_account_private
from app.services.follows import follow_user
from app.services.exceptions import UserNotFoundError, \
    AccountAlreadyPrivateError, AccountAlreadyPublicError
# from app.models import User
from app.core.constants import FOLLOW_ACCEPTED_TXT, FOLLOW_PENDING_TXT
from tests.helpers import create_user


def test_make_account_private(db: Session) -> None:
    user = create_user(db, "user")
    make_account_private(db, user.id)
    db.refresh(user)
    assert user.is_private == True, \
        "The account was not set to private."


def test_user_not_found_make_account_private_error(db: Session) -> None:
    unknown_user_id = -1000
    with pytest.raises(UserNotFoundError):
        make_account_private(db, unknown_user_id)


def test_already_private_error(db: Session) -> None:
    private = create_user(db, "user", is_private=True)
    with pytest.raises(AccountAlreadyPrivateError):
        make_account_private(db, private.id)


def test_make_account_public(db: Session) -> None:
    user = create_user(db, "user", is_private=True)
    make_account_public(db, user.id)
    db.refresh(user)
    assert user.is_private == False, \
        "The account was not set to public."


def test_make_account_public_pending_follows(db: Session) -> None:
    private_1 = create_user(db, "private1", is_private=True)
    private_2 = create_user(db, "private2", is_private=True)
    follower = create_user(db, "follower")
    follow_1 = follow_user(db, follower.id, private_1.id)
    follow_2 = follow_user(db, follower.id, private_2.id)
    make_account_public(db, private_1.id)
    db.refresh(follow_1)
    db.refresh(follow_2)
    assert follow_1.status == FOLLOW_ACCEPTED_TXT, \
        f"The follows to this account were not set to '{FOLLOW_ACCEPTED_TXT}'"
    assert follow_2.status == FOLLOW_PENDING_TXT, \
        f"The follows to this account are not suppossed to be set to " \
        f"'{FOLLOW_ACCEPTED_TXT}'"


def test_user_not_found_make_account_public_error(db: Session) -> None:
    unknown_user_id = -1000
    with pytest.raises(UserNotFoundError):
        make_account_public(db, unknown_user_id)


def test_already_public_error(db: Session) -> None:
    public = create_user(db, "user")
    with pytest.raises(AccountAlreadyPublicError):
        make_account_public(db, public.id)
