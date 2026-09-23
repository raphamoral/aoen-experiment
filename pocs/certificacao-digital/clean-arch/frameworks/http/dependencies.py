from typing import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from adapters.controllers.certificate_controller import CertificateController
from adapters.controllers.course_controller import CourseController
from adapters.controllers.issuer_controller import IssuerController
from adapters.controllers.student_controller import StudentController
from frameworks.db.database import SessionLocal
from frameworks.repositories.sqlalchemy_certificate_repository import SQLAlchemyCertificateRepository
from frameworks.repositories.sqlalchemy_course_repository import SQLAlchemyCourseRepository
from frameworks.repositories.sqlalchemy_issuer_repository import SQLAlchemyIssuerRepository
from frameworks.repositories.sqlalchemy_student_repository import SQLAlchemyStudentRepository
from use_cases.issue_certificate import IssueCertificateUseCase
from use_cases.list_student_certificates import ListStudentCertificatesUseCase
from use_cases.register_course import RegisterCourseUseCase
from use_cases.register_issuer import RegisterIssuerUseCase
from use_cases.register_student import RegisterStudentUseCase
from use_cases.revoke_certificate import RevokeCertificateUseCase
from use_cases.verify_certificate import VerifyCertificateUseCase


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_certificate_controller(db: Session = Depends(get_db)) -> CertificateController:
    cert_repo = SQLAlchemyCertificateRepository(db)
    course_repo = SQLAlchemyCourseRepository(db)
    student_repo = SQLAlchemyStudentRepository(db)
    return CertificateController(
        issue_uc=IssueCertificateUseCase(cert_repo, course_repo, student_repo),
        verify_uc=VerifyCertificateUseCase(cert_repo),
        revoke_uc=RevokeCertificateUseCase(cert_repo),
        list_uc=ListStudentCertificatesUseCase(cert_repo, student_repo),
    )


def get_course_controller(db: Session = Depends(get_db)) -> CourseController:
    return CourseController(
        register_uc=RegisterCourseUseCase(
            course_repo=SQLAlchemyCourseRepository(db),
            issuer_repo=SQLAlchemyIssuerRepository(db),
        )
    )


def get_student_controller(db: Session = Depends(get_db)) -> StudentController:
    return StudentController(
        register_uc=RegisterStudentUseCase(SQLAlchemyStudentRepository(db))
    )


def get_issuer_controller(db: Session = Depends(get_db)) -> IssuerController:
    return IssuerController(
        register_uc=RegisterIssuerUseCase(SQLAlchemyIssuerRepository(db))
    )