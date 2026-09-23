from datetime import date

from src.repositories.exam_repository import ExamRepository
from src.repositories.nutrition_repository import NutritionPlanRepository
from src.repositories.user_repository import UserRepository
from src.services.ai_service import get_ai_provider
from src.config import settings


class NutritionService:
    def __init__(
        self,
        user_repo: UserRepository,
        exam_repo: ExamRepository,
        plan_repo: NutritionPlanRepository,
    ) -> None:
        self.user_repo = user_repo
        self.exam_repo = exam_repo
        self.plan_repo = plan_repo

    async def generate_plan(self, user_id: int, exam_panel_id: int | None = None) -> dict:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            return {"error": "Usuário não encontrado"}

        user_data = {
            "nome": user.name,
            "idade": self._calc_age(user.birth_date),
            "sexo": user.sex.value,
            "altura_cm": user.height_cm,
            "peso_kg": user.weight_kg,
            "nivel_atividade": user.activity_level.value,
            "objetivos": user.health_goals,
        }

        exam_data: dict = {}
        if exam_panel_id:
            panel = await self.exam_repo.get_by_id(exam_panel_id)
            if panel:
                exam_data = {
                    r.marker_name: {"valor": r.value, "status": r.status}
                    for r in panel.results
                }

        provider = get_ai_provider()
        plan_data = await provider.generate_nutrition_plan(user_data, exam_data)

        saved = await self.plan_repo.create(
            user_id=user_id,
            exam_panel_id=exam_panel_id,
            deficiencies=plan_data.get("deficiencias", []),
            recommendations=plan_data.get("recomendacoes", []),
            restrictions=plan_data.get("restricoes", []),
            supplements=plan_data.get("suplementos", []),
            daily_calories=plan_data.get("meta_calorica"),
            macros=plan_data.get("macros"),
            ai_provider_used=settings.AI_PROVIDER,
        )

        return {**plan_data, "plan_id": saved.id}

    async def get_plan(self, plan_id: int):
        return await self.plan_repo.get_by_id(plan_id)

    async def list_user_plans(self, user_id: int):
        return await self.plan_repo.list_by_user(user_id)

    @staticmethod
    def _calc_age(birth_date) -> int:
        today = date.today()
        return today.year - birth_date.year - (
            (today.month, today.day) < (birth_date.month, birth_date.day)
        )