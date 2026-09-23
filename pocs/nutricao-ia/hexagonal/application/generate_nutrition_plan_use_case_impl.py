from domain.entities.nutrition_plan import NutritionPlan
from domain.exceptions import DomainValidationError, LabExamNotFoundError, PatientNotFoundError
from domain.services.nutrition_analysis_service import NutritionAnalysisService
from ports.input.generate_nutrition_plan_use_case import (
    GenerateNutritionPlanCommand,
    GenerateNutritionPlanUseCasePort,
)
from ports.output.ai_analysis_provider_port import AIAnalysisProviderPort
from ports.output.lab_exam_repository_port import LabExamRepositoryPort
from ports.output.notification_service_port import NotificationServicePort
from ports.output.nutrition_plan_repository_port import NutritionPlanRepositoryPort
from ports.output.patient_repository_port import PatientRepositoryPort


class GenerateNutritionPlanUseCaseImpl(GenerateNutritionPlanUseCasePort):
    def __init__(
        self,
        patient_repo: PatientRepositoryPort,
        lab_exam_repo: LabExamRepositoryPort,
        nutrition_plan_repo: NutritionPlanRepositoryPort,
        analysis_service: NutritionAnalysisService,
        ai_provider: AIAnalysisProviderPort,
        notification_service: NotificationServicePort,
    ) -> None:
        self._patient_repo = patient_repo
        self._lab_exam_repo = lab_exam_repo
        self._nutrition_plan_repo = nutrition_plan_repo
        self._analysis_service = analysis_service
        self._ai_provider = ai_provider
        self._notification_service = notification_service

    async def execute(self, command: GenerateNutritionPlanCommand) -> NutritionPlan:
        patient = await self._patient_repo.find_by_id(command.patient_id)
        if not patient:
            raise PatientNotFoundError(command.patient_id)

        exam = await self._lab_exam_repo.find_by_id(command.lab_exam_id)
        if not exam:
            raise LabExamNotFoundError(command.lab_exam_id)
        if exam.patient_id != command.patient_id:
            raise DomainValidationError("Exam does not belong to the specified patient")

        # Pure domain logic — no I/O
        recommendations, findings = self._analysis_service.analyze_exam(exam, patient)

        # External I/O via secondary port (AI is just another adapter)
        ai_analysis = await self._ai_provider.analyze(patient, exam, findings)

        plan = NutritionPlan(
            patient_id=patient.id,
            lab_exam_id=exam.id,
            recommendations=recommendations,
            general_notes="\n".join(findings),
            ai_analysis=ai_analysis,
        )

        saved_plan = await self._nutrition_plan_repo.save(plan)
        await self._notification_service.send_plan_ready(patient, saved_plan)
        return saved_plan