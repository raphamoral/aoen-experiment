from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from entities.student import Student
from frameworks.db.models import StudentModel
from use_cases.ports.student_repository import StudentRepository


class SQLAlchemyStudentRepository(StudentRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, student: Student) -> Student:
        model = StudentModel(
            id=str(student.id),
            name=student.name,
            email=student.email,
        )
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    def find_by_id(self, student_id: UUID) -> Optional[Student]:
        model = self._session.query(StudentModel).filter_by(id=str(student_id)).first()
        return self._to_entity(model) if model else None

    def find_by_email(self, email: str) -> Optional[Student]:
        model = self._session.query(StudentModel).filter_by(email=email).first()
        return self._to_entity(model) if model else None

    @staticmethod
    def _to_entity(model: StudentModel) -> Student:
        return Student(id=UUID(model.id), name=model.name, email=model.email)