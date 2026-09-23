from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class IssuerModel(Base):
    __tablename__ = "issuers"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    document = Column(String, nullable=False, unique=True, index=True)

    courses = relationship("CourseModel", back_populates="issuer")


class CourseModel(Base):
    __tablename__ = "courses"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    issuer_id = Column(String, ForeignKey("issuers.id"), nullable=False)
    workload_hours = Column(Integer, nullable=False)

    issuer = relationship("IssuerModel", back_populates="courses")
    certificates = relationship("CertificateModel", back_populates="course")


class StudentModel(Base):
    __tablename__ = "students"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)

    certificates = relationship("CertificateModel", back_populates="student")


class CertificateModel(Base):
    __tablename__ = "certificates"

    id = Column(String, primary_key=True)
    student_id = Column(String, ForeignKey("students.id"), nullable=False, index=True)
    course_id = Column(String, ForeignKey("courses.id"), nullable=False)
    issuer_id = Column(String, ForeignKey("issuers.id"), nullable=False)
    issued_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    verification_hash = Column(String, nullable=False, unique=True, index=True)
    is_valid = Column(Boolean, nullable=False, default=True)

    student = relationship("StudentModel", back_populates="certificates")
    course = relationship("CourseModel", back_populates="certificates")