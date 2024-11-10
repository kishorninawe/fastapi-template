import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Integer,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.common.enums import GenderEnum
from app.core.config import settings
from app.sqltypes import EncryptedText


class Base(DeclarativeBase):
    __table_args__ = {"schema": settings.POSTGRES_SCHEMA}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


class User(Base):
    __tablename__ = "user"

    email: Mapped[bytes] = mapped_column(EncryptedText(), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(Text(), nullable=False)
    gender: Mapped[str] = mapped_column(Enum(GenderEnum, name="gender_enum"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=True)
    date_joined: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp()
    )
    last_login: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp()
    )
    last_active: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )

    # The key version indicates the encryption key version used for encrypting the data.
    # It aids in key rotation by allowing the correct decryption key to be identified based on the version.
    # No need to write this if the table doesn't contain an encrypted column.
    key_version: Mapped[int] = mapped_column(Integer(), nullable=False)

    def __repr__(self) -> str:
        return f"User(email={self.email})"
