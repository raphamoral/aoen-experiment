"""
Composition Root — the only module that knows about all layers simultaneously.

This module wires ports to their adapter implementations and provides
FastAPI dependency factories for use case injection into HTTP adapters.
"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from adapters.output.ai.claude_analysis_provider import ClaudeAnalysisProvider
from adapters.output.notification.smtp_notification_service import SMTPNotificationService
from adapters.output.persistence.sqlalchemy_lab_exam_repository import SQLAlchemyLabExamRepository
from adapters.output.persistence.sqlalchemy_nutrition_plan_repository import SQLAlchemyNutritionPlanRepository
from adapters.output.persistence.sqlalchemy_patient_repository import SQLAlchemyPatientRepository
from application.generate_nutrition_plan_use_case_impl import GenerateNutritionPlanUseCaseImpl
from application.get_nutrition_plan_use_case_impl import GetNutritionPlanUseCaseImpl
from application.register_patient_use_case_impl import RegisterPatientUseCaseImpl
from application.submit_lab_exam_use_case_impl import SubmitLabExamUseCaseImpl
from config.database import get_session
from config.settings import Settings, get_settings
from domain.services.nutrition_analysis_service import NutritionAnalysisService
from ports.input.generate_nutrition_plan_use_case import GenerateNutritionPlanUseCasePort
from ports.input.get_nutrition_plan_use_case import GetNutritionPlanUseCasePort
from ports.input.register_patient_use_case import RegisterPatientUseCasePort
from ports.input.submit_lab_exam_use_case import SubmitLabExamUseCasePort


def get_notification_service(
    settings: Settings = Depends(get_settings),
) -> SMTPNotificationService:
    return SMTPNotificationService(
        host=settings.smtp_host,
        port=settings.smtp_port,
        username=settings.smtp_username,
        password=settings.smtp_password,
        sender_email=settings.smtp_sender_email,
        use_tls=settings.smtp_use_tls,
    )


def get_ai_provider(
    settings: Settings = Depends(get_settings),
) -> ClaudeAnalysisProvider:
    return ClaudeAnalysisProvider(
        api_key=settings.anthropic_api_key,
        model=settings.anthropic_model,
    )


def get_register_patient_use_case(
    session: AsyncSession = Depends(get_session),
    notification_service: SMTPNotificationService = Depends(get_notification_service),
) -> RegisterPatientUseCasePort:
    return RegisterPatientUseCaseImpl(
        patient_repo=SQLAlchemyPatientRepository(session),
        notification_service=notification_service,
    )


def get_submit_lab_exam_use_case(
    session: AsyncSession = Depends(get_session),
) -> SubmitLabExamUseCasePort:
    return SubmitLabExamUseCaseImpl(
        patient_repo=SQLAlchemyPatientRepository(session),
        lab_exam_repo=SQLAlchemyLabExamRepository(session),
    )


def get_generate_nutrition_plan_use_case(
    session: AsyncSession = Depends(get_session),
    ai_provider: ClaudeAnalysisProvider = Depends(get_ai_provider),
    notification_service: SMTPNotificationService = Depends(get_notification_service),
) -> GenerateNutritionPlanUseCasePort:
    return GenerateNutritionPlanUseCaseImpl(
        patient_repo=SQLAlchemyPatientRepository(session),
        lab_exam_repo=SQLAlchemyLabExamRepository(session),
        nutrition_plan_repo=SQLAlchemyNutritionPlanRepository(session),
        analysis_service=NutritionAnalysisService(),
        ai_provider=ai_provider,
        notification_service=notification_service,
    )


def get_nutrition_plan_use_case(
    session: AsyncSession = Depends(get_session),
) -> GetNutritionPlanUseCasePort:
    return GetNutritionPlanUseCaseImpl(
        nutrition_plan_repo=SQLAlchemyNutritionPlanRepository(session),
    )