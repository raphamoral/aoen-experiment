from datetime import datetime

from src.models.exam import ExamPanel
from src.repositories.exam_repository import ExamRepository
from src.services.ai_service import get_ai_provider


class ExamService:
    def __init__(self, repo: ExamRepository) -> None:
        self.repo = repo

    async def register_panel(
        self,
        user_id: int,
        exam_date: datetime,
        lab_name: str,
        notes: str,
        results: list[dict],
    ) -> ExamPanel:
        return await self.repo.create_with_results(
            user_id=user_id,
            exam_date=exam_date,
            lab_name=lab_name,
            notes=notes,
            results=results,
        )

    async def get_panel(self, panel_id: int) -> ExamPanel | None:
        return await self.repo.get_by_id(panel_id)

    async def list_user_panels(self, user_id: int) -> list[ExamPanel]:
        return await self.repo.list_by_user(user_id)

    async def analyze_deficiencies(self, panel_id: int) -> dict:
        panel = await self.repo.get_by_id(panel_id)
        if not panel:
            return {"error": "Painel não encontrado"}

        exam_data = {
            r.marker_name: {
                "valor": r.value,
                "unidade": r.unit,
                "status": r.status,
                "referencia_min": r.reference_min,
                "referencia_max": r.reference_max,
            }
            for r in panel.results
        }

        provider = get_ai_provider()
        return await provider.analyze_deficiencies(exam_data)