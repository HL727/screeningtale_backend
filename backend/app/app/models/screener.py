from typing import TYPE_CHECKING
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base

if TYPE_CHECKING:
    from .users import User  # noqa: F401


class Screener(Base):
    __tablename__ = "screener"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    criteria = Column(String, nullable=False)
    creator_id = Column(Integer, ForeignKey("users.id"))
    creator = relationship("User", back_populates="screeners")
