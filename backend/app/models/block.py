"""
Each class represents a SQL table
"""

from sqlalchemy import Column, Integer, DateTime, \
    func, ForeignKey, CheckConstraint

from ..database import Base


class Block(Base):
    __tablename__ = "blocks"

    blocker_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"),
                        primary_key=True)
    blocked_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"),
                        primary_key=True,
                        index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("blocker_id <> blocked_id",
                        name="disallow_autoblock"),
    )
