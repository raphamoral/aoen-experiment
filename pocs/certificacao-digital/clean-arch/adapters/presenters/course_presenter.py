from entities.course import Course
from adapters.schemas.course_schema import CourseResponse


class CoursePresenter:

    @staticmethod
    def to_response(course: Course) -> CourseResponse:
        return CourseResponse(
            id=course.id,
            name=course.name,
            description=course.description,
            issuer_id=course.issuer_id,
            workload_hours=course.workload_hours,
        )