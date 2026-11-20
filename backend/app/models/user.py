"""
Each class represents a SQL table
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, \
    text, func

from ..database import Base
from ..core.constants import USERNAME_MAX_LEN, EMAIL_MAX_LEN, \
    HASHED_PASSWORD_MAX_LEN, DEFAULT_AVATAR, URL_MAX_LEN


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(USERNAME_MAX_LEN),
                      unique=True, index=True, nullable=False)
    email = Column(String(EMAIL_MAX_LEN),
                   unique=True, index=True, nullable=False)
    hashed_password = Column(String(HASHED_PASSWORD_MAX_LEN), nullable=False)

    avatar_url = Column(String(URL_MAX_LEN),
                        default=DEFAULT_AVATAR)
    is_active = Column(Boolean, server_default=text("true"), nullable=False)
    is_private = Column(Boolean, server_default=text("false"), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
