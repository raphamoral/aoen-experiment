# Importar todos os modelos para que o metadata do SQLAlchemy os conheça em create_all.
from src.models.base import Base
from src.models.exam import ExamPanel, ExamResult
from src.models.nutrition import NutritionPlan
from src.models.user import User

__all__ = ["Base", "User", "ExamPanel", "ExamResult", "NutritionPlan"]