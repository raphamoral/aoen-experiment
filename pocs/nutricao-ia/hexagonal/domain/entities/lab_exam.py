from dataclasses import dataclass, field
from datetime import date, datetime
from uuid import UUID, uuid4


@dataclass
class ExamResult:
    exam_type: str
    value: float
    unit: str
    reference_min: float | None = None
    reference_max: float | None = None

    @property
    def is_below_range(self) -> bool:
        return self.reference_min is not None and self.value < self.reference_min

    @property
    def is_above_range(self) -> bool:
        return self.reference_max is not None and self.value > self.reference_max

    @property
    def is_normal(self) -> bool:
        return not self.is_below_range and not self.is_above_range


@dataclass
class LabExam:
    patient_id: UUID
    exam_date: date
    results: list[ExamResult]
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def get_result(self, exam_type: str) -> ExamResult | None:
        for result in self.results:
            if result.exam_type == exam_type:
                return result
        return None

    def get_abnormal_results(self) -> list[ExamResult]:
        return [r for r in self.results if not r.is_normal]