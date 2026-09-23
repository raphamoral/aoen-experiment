from dataclasses import dataclass
from typing import List, Optional

from entities.exam import Exam
from entities.nutrition_plan import NutritionPlan
from entities.patient import Patient
from use_cases.ports.exam_repository_port import ExamRepositoryPort
from use_cases.ports.nutrition_plan_repository_port import NutritionPlanRepositoryPort
from use_cases.ports.patient_repository_port import PatientRepositoryPort


@dataclass
class GetPatientReportInput:
    patient_id: str


@dataclass
class PatientReport:
    patient: Patient
    exams: List[Exam]
    latest_nutrition_plan: Optional[NutritionPlan]
    total_exams: int
    has_critical_markers: bool


class GetPatientReport:
    def __init__(
        self,
        patient_repository: PatientRepositoryPort,
        exam_repository: ExamRepositoryPort,
        nutrition_plan_repository: NutritionPlanRepositoryPort,
    ) -> None:
        self._patient_repo = patient_repository
        self._exam_repo = exam_repository
        self._plan_repo = nutrition_plan_repository

    def execute(self, input_data: GetPatientReportInput) -> PatientReport:
        patient = self._patient_repo.find_by_id(input_data.patient_id)
        if not patient:
            raise ValueError(f"Paciente {input_data.patient_id} não encontrado")

        exams = self._exam_repo.find_by_patient_id(input_data.patient_id)
        latest_plan = self._plan_repo.find_latest_by_patient_id(input_data.patient_id)
        has_critical = any(exam.critical_markers for exam in exams)

        return PatientReport(
            patient=patient,
            exams=exams,
            latest_nutrition_plan=latest_plan,
            total_exams=len(exams),
            has_critical_markers=has_critical,
        )