from datetime import datetime
from typing import Annotated, Optional
from uuid import UUID

from pydantic import Field
from sqlalchemy import String, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.functions import now

from yatt.models import AppBaseModel
from yatt.core import Base


# ORM
class User(Base):
    """SQLAlchemy model for users resource"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[UUID] = mapped_column(Uuid, unique=True)
    login: Mapped[str] = mapped_column(String(50), unique=True)
    email: Mapped[Optional[str]] = mapped_column(String(50))
    password: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=now())


# Pydantic models
Password = Annotated[str, Field(max_length=100)]
Email = Annotated[str, Field(max_length=50)]


class UserBase(AppBaseModel):
    """Base user data model"""

    login: str = Field(max_length=50)
    email: Optional[Email]


class UserCreateParams(UserBase):
    """Data model for creating new user"""

    password: Password


class UserPatchParams(AppBaseModel):
    """Data model for user update params"""

    email: Optional[Email]


class UserSetPasswordParams(AppBaseModel):
    """Data model for updating user password"""

    password: Password


class UserView(UserBase):
    """Data model for generic user response"""

    uuid: UUID
