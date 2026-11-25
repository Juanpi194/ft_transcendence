"""
Each class represents a SQL table
"""

from sqlalchemy import Column, Integer, String, DateTime, \
    ForeignKey, CheckConstraint, func

from ..database import Base
from ..core.constants import STATUS_MAX_LEN, FOLLOW_ACCEPTED_TXT, \
    FOLLOW_PENDING_TXT


class Follow(Base):
    __tablename__ = "follows"

    follower_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"),
                         primary_key=True)
    followed_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"),
                         primary_key=True, 
                         index=True)
    status = Column(String(STATUS_MAX_LEN), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("follower_id <> followed_id",
                        name="disallow_autofollow"),
        CheckConstraint(
            f"status IN ('{FOLLOW_ACCEPTED_TXT}', '{FOLLOW_PENDING_TXT}')",
            name="status_accepted_values"),
    )
