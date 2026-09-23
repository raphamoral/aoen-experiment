from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List

from use_cases.submit_exam_results import ExamMarkerInput, SubmitExamInput, SubmitExamResults


@dataclass
class ExamMarkerRequest:
    name: str
    value: float
    unit: str
    reference_min: float
    reference_max: float


@dataclass
class SubmitExamRequest:
    patient_id: str
    exam_date: datetime
    lab_name: str
    markers: List[ExamMarkerRequest] = field(default_factory=list)


class ExamController:
    def __init__(self, submit_exam: SubmitExamResults) -> None:
        self._submit_exam = submit_exam

    def submit(self, request: SubmitExamRequest) -> Dict[str, Any]:
        output = self._submit_exam.execute(
            SubmitExamInput(
                patient_id=request.patient_id,
                exam_date=request.exam_date,
                lab_name=request.lab_name,
                markers=[
                    ExamMarkerInput(
                        name=m.name,
                        value=m.value,
                        unit=m.unit,
                        reference_min=m.reference_min,
                        reference_max=m.reference_max,
                    )
                    for m in request.markers
                ],
            )
        )
        exam = output.exam
        return {
            "id": exam.id,
            "patient_id": exam.patient_id,
            "exam_date": exam.exam_date.isoformat(),
            "lab_name": exam.lab_name,
            "total_markers": len(exam.markers),
            "abnormal_count": output.abnormal_count,
            "critical_count": output.critical_count,
            "markers": [
                {
                    "name": m.name,
                    "value": m.value,
                    "unit": m.unit,
                    "reference_min": m.reference_min,
                    "reference_max": m.reference_max,
                    "status": m.status.value,
                    "deviation_percentage": m.deviation_percentage,
                }
                for m in exam.markers
            ],
        }