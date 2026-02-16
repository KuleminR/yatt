from datetime import datetime
from typing import Optional
from uuid import UUID

from yatt.core import Base

from sqlalchemy import String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

# ORM


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[UUID] = mapped_column(Uuid)
    name: Mapped[str] = mapped_column(String(50))
    email: Mapped[Optional[str]] = mapped_column(String(50))
    password: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime]


# Pydantic models
