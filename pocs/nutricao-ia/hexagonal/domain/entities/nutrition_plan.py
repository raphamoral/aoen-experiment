from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from domain.value_objects.nutrient_level import NutrientLevel


@dataclass
class DietaryRecommendation:
    nutrient: str
    level: NutrientLevel
    foods_to_increase: list[str]
    foods_to_avoid: list[str]
    supplements: list[str]
    clinical_notes: str


@dataclass
class NutritionPlan:
    patient_id: UUID
    lab_exam_id: UUID
    recommendations: list[DietaryRecommendation]
    general_notes: str
    ai_analysis: str
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def has_critical_deficiencies(self) -> bool:
        return any(r.level == NutrientLevel.DEFICIENT for r in self.recommendations)

    @property
    def abnormal_nutrients(self) -> list[str]:
        return [
            r.nutrient
            for r in self.recommendations
            if r.level != NutrientLevel.NORMAL
        ]