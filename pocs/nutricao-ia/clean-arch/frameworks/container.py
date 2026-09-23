import os

from fastapi import Depends
from sqlalchemy.orm import Session

from adapters.controllers.exam_controller import ExamController
from adapters.controllers.nutrition_controller import NutritionController
from adapters.controllers.patient_controller import PatientController
from frameworks.ai.anthropic_service import AnthropicNutritionService
from frameworks.db.connection import get_db
from frameworks.db.repositories.exam_repository import SqlAlchemyExamRepository
from frameworks.db.repositories.nutrition_plan_repository import SqlAlchemyNutritionPlanRepository
from frameworks.db.repositories.patient_repository import SqlAlchemyPatientRepository
from use_cases.generate_nutrition_plan import GenerateNutritionPlan
from use_cases.get_patient_report import GetPatientReport
from use_cases.register_patient import RegisterPatient
from use_cases.submit_exam_results import SubmitExamResults


# ── Repositories ──────────────────────────────────────────────────────────────

def get_patient_repository(db: Session = Depends(get_db)) -> SqlAlchemyPatientRepository:
    return SqlAlchemyPatientRepository(db)


def get_exam_repository(db: Session = Depends(get_db)) -> SqlAlchemyExamRepository:
    return SqlAlchemyExamRepository(db)


def get_nutrition_plan_repository(db: Session = Depends(get_db)) -> SqlAlchemyNutritionPlanRepository:
    return SqlAlchemyNutritionPlanRepository(db)


# ── External services ─────────────────────────────────────────────────────────

def get_ai_service() -> AnthropicNutritionService:
    return AnthropicNutritionService(api_key=os.environ["ANTHROPIC_API_KEY"])


# ── Controllers (wire use cases + repositories) ───────────────────────────────

def get_patient_controller(
    patient_repo: SqlAlchemyPatientRepository = Depends(get_patient_repository),
    exam_repo: SqlAlchemyExamRepository = Depends(get_exam_repository),
    plan_repo: SqlAlchemyNutritionPlanRepository = Depends(get_nutrition_plan_repository),
) -> PatientController:
    return PatientController(
        register_patient=RegisterPatient(patient_repository=patient_repo),
        get_patient_report=GetPatientReport(
            patient_repository=patient_repo,
            exam_repository=exam_repo,
            nutrition_plan_repository=plan_repo,
        ),
    )


def get_exam_controller(
    patient_repo: SqlAlchemyPatientRepository = Depends(get_patient_repository),
    exam_repo: SqlAlchemyExamRepository = Depends(get_exam_repository),
) -> ExamController:
    return ExamController(
        submit_exam=SubmitExamResults(
            patient_repository=patient_repo,
            exam_repository=exam_repo,
        )
    )


def get_nutrition_controller(
    patient_repo: SqlAlchemyPatientRepository = Depends(get_patient_repository),
    exam_repo: SqlAlchemyExamRepository = Depends(get_exam_repository),
    plan_repo: SqlAlchemyNutritionPlanRepository = Depends(get_nutrition_plan_repository),
    ai_service: AnthropicNutritionService = Depends(get_ai_service),
) -> NutritionController:
    return NutritionController(
        generate_plan=GenerateNutritionPlan(
            patient_repository=patient_repo,
            exam_repository=exam_repo,
            nutrition_plan_repository=plan_repo,
            ai_service=ai_service,
        )
    )