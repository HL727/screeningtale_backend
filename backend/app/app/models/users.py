from typing import TYPE_CHECKING
from sqlalchemy.orm import relationship
from app.db.base import Base
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects import postgresql

if TYPE_CHECKING:
    from .screener import Screener  # noqa: F401


class MemberDefinition(str, Enum):
    FREE = "FREE"
    PREMIUM = "PREMIUM"
    ELITE = "ELITE"


class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True)
    compound_id = Column(String(256), nullable=False, index=True, unique=True)
    user_id = Column(Integer, nullable=False, index=True)
    provider_type = Column(String(256), nullable=False)
    provider_id = Column(String(256), nullable=False, index=True)
    provider_account_id = Column(String(256), nullable=False, index=True)
    refresh_token = Column(Text)
    access_token = Column(Text)
    access_token_expires = Column(postgresql.TIMESTAMP(timezone=True))
    created_at = Column(
        postgresql.TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
    )
    updated_at = Column(
        postgresql.TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
    )


class Sessions(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    expires = Column(postgresql.TIMESTAMP(timezone=True), nullable=False)
    session_token = Column(String(256), nullable=False, index=True, unique=True)
    access_token = Column(String(256), nullable=False, index=True, unique=True)
    created_at = Column(
        postgresql.TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
    )
    updated_at = Column(
        postgresql.TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
    )


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(256))
    email = Column(String(256), index=True, unique=True)
    email_verified = Column(postgresql.TIMESTAMP(timezone=True))
    image = Column(Text)
    created_at = Column(
        postgresql.TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
    )
    updated_at = Column(
        postgresql.TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
    )
    member_role = Column(
        postgresql.ENUM(MemberDefinition, create_type=False),
        server_default="{FREE}",
        nullable=False,
    )
    screeners = relationship("Screener", back_populates="creator")
    password = Column(String(120))
    email_verified_status = Column(Boolean)
    verify_token = relationship("VerificationToken", cascade="all,delete", backref="users")
    subscription_id = Column(String(60), default=None)
    customer_id = Column(String(20), default=None)


class VerificationRequest(Base):
    __tablename__ = "verification_requests"
    id = Column(Integer, primary_key=True)
    identifier = Column(String(256))
    token = Column(String(256), index=True, unique=True)
    expires = Column(postgresql.TIMESTAMP(timezone=True), nullable=False)
    created_at = Column(
        postgresql.TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
    )
    updated_at = Column(
        postgresql.TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
    )


class VerificationToken(Base):
    __tablename__ = "verification_token"
    id = Column(Integer, primary_key=True)
    user = Column(Integer, ForeignKey("users.id"))
    token = Column(String(120), unique=True)
    created_at = Column(
        postgresql.TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
    )


class PasswordResetToken(Base):
    __tablename__ = "password_reset_token"
    id = Column(Integer, primary_key=True)
    user = Column(Integer, ForeignKey("users.id"))
    token = Column(String(120), unique=True)
    created_at = Column(
        postgresql.TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
    )