import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.infrastructure.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class Course(Base):
    __tablename__ = "courses"

    id = Column(String, primary_key=True, default=_uuid)
    name = Column(String(255), nullable=False)
    instructor = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    duration_hours = Column(Integer, nullable=False)
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    certificates = relationship("Certificate", back_populates="course")


class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(String, primary_key=True, default=_uuid)
    course_id = Column(String, ForeignKey("courses.id"), nullable=False)
    recipient_name = Column(String(255), nullable=False)
    recipient_email = Column(String(255), nullable=False)
    issued_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    verification_hash = Column(String(64), unique=True, nullable=False, index=True)
    revoked = Column(Boolean, default=False, nullable=False)
    revoked_at = Column(DateTime, nullable=True)

    course = relationship("Course", back_populates="certificates")