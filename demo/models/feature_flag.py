from typing import Optional

from sqlalchemy import Boolean, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel


class FeatureFlag(BaseModel):
    __tablename__ = "feature_flag"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    description: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    environment: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="dev",
    )

    __table_args__ = (
        UniqueConstraint("name", "environment", name="uq_flag_name_env"),
        Index("ix_flag_environment", "environment"),
    )

    def __init__(
        self,
        name: str,
        enabled: bool = False,
        environment: str = "dev",
        description: str | None = None,
    ) -> None:
        self.name = name
        self.enabled = enabled
        self.environment = environment
        self.description = description

    def toggle(self) -> None:
        self.enabled = not self.enabled

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "enabled": self.enabled,
            "description": self.description,
            "environment": self.environment,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
