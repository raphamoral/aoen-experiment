from dataclasses import dataclass

from entities.nutrition_plan import NutritionPlan
from use_cases.ports.ai_nutrition_service_port import AiNutritionServicePort
from use_cases.ports.exam_repository_port import ExamRepositoryPort
from use_cases.ports.nutrition_plan_repository_port import NutritionPlanRepositoryPort
from use_cases.ports.patient_repository_port import PatientRepositoryPort


@dataclass
class GenerateNutritionPlanInput:
    patient_id: str
    exam_id: str


@dataclass
class GenerateNutritionPlanOutput:
    plan: NutritionPlan


class GenerateNutritionPlan:
    def __init__(
        self,
        patient_repository: PatientRepositoryPort,
        exam_repository: ExamRepositoryPort,
        nutrition_plan_repository: NutritionPlanRepositoryPort,
        ai_service: AiNutritionServicePort,
    ) -> None:
        self._patient_repo = patient_repository
        self._exam_repo = exam_repository
        self._plan_repo = nutrition_plan_repository
        self._ai_service = ai_service

    def execute(self, input_data: GenerateNutritionPlanInput) -> GenerateNutritionPlanOutput:
        patient = self._patient_repo.find_by_id(input_data.patient_id)
        if not patient:
            raise ValueError(f"Paciente {input_data.patient_id} não encontrado")

        exam = self._exam_repo.find_by_id(input_data.exam_id)
        if not exam:
            raise ValueError(f"Exame {input_data.exam_id} não encontrado")

        if exam.patient_id != patient.id:
            raise ValueError("Exame não pertence a este paciente")

        plan = self._ai_service.generate_plan(patient, exam)
        plan.validate()

        saved = self._plan_repo.save(plan)
        return GenerateNutritionPlanOutput(plan=saved)