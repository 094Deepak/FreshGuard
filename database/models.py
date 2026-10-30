from datetime import datetime

from sqlalchemy import Float, Integer, String, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from database.database import Base


class Batch(Base):

    __tablename__ = "batches"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    batch_code: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False,
    )

    product_name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    temperature: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    humidity: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    remaining_shelf_life: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )


class Alert(Base):

    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    batch_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )

    batch_code: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    product_name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    severity: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    message: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    estimated_remaining_shelf_life: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    environmental_stress_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    recommendation: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    resolved: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # Human-in-the-Loop fields

    review_status: Mapped[str] = mapped_column(
        String,
        default="Pending",
        nullable=False,
    )

    human_decision: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    review_comment: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )