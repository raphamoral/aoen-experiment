from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from adapters.outbound.persistence.database import Base


class CertificateModel(Base):
    __tablename__ = "certificates"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    student_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    course_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    student_name: Mapped[str] = mapped_column(String, nullable=False)
    course_name: Mapped[str] = mapped_column(String, nullable=False)
    issuer_name: Mapped[str] = mapped_column(String, nullable=False)
    duration_hours: Mapped[int] = mapped_column(Integer, nullable=False)
    issued_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    certificate_hash: Mapped[str] = mapped_column(
        String, unique=True, nullable=False, index=True
    )
    is_valid: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    revocation_reason: Mapped[Optional[str]] = mapped_column(String, nullable=True)