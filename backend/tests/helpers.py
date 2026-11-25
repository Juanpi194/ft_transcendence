from sqlalchemy.orm import Session

from app.models import User, Block


def create_user(db: Session, username: str, is_private: bool = False) -> User:
    """
    Creates a user for the database. It does add it and commit it.
    """
    user = User(username=username,
                email=f"{username}@test.com",
                hashed_password="default_password",
                is_private=is_private)
    db.add(user)
    db.commit()
    return user


def create_block(db: Session, blocker: User, blocked: User) -> Block:
    """
    Creates a block for the database. It does add it and commit it.
    """
    block = Block(blocker_id=blocker.id,
                  blocked_id=blocked.id)
    db.add(block)
    db.commit()
    return block
