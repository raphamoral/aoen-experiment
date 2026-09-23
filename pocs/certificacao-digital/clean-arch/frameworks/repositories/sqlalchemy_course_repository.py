from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from entities.course import Course
from frameworks.db.models import CourseModel
from use_cases.ports.course_repository import CourseRepository


class SQLAlchemyCourseRepository(CourseRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, course: Course) -> Course:
        model = CourseModel(
            id=str(course.id),
            name=course.name,
            description=course.description,
            issuer_id=str(course.issuer_id),
            workload_hours=course.workload_hours,
        )
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    def find_by_id(self, course_id: UUID) -> Optional[Course]:
        model = self._session.query(CourseModel).filter_by(id=str(course_id)).first()
        return self._to_entity(model) if model else None

    def find_by_issuer_id(self, issuer_id: UUID) -> list[Course]:
        models = (
            self._session.query(CourseModel)
            .filter_by(issuer_id=str(issuer_id))
            .all()
        )
        return [self._to_entity(m) for m in models]

    @staticmethod
    def _to_entity(model: CourseModel) -> Course:
        return Course(
            id=UUID(model.id),
            name=model.name,
            description=model.description,
            issuer_id=UUID(model.issuer_id),
            workload_hours=model.workload_hours,
        )