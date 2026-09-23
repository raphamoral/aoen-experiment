from dataclasses import dataclass
from enum import Enum


class NutrientCategory(str, Enum):
    MACRONUTRIENT = "macronutrient"
    VITAMIN = "vitamin"
    MINERAL = "mineral"
    FATTY_ACID = "fatty_acid"


@dataclass
class Nutrient:
    name: str
    category: NutrientCategory
    daily_target_g: float
    unit: str
    reason: str

    def validate(self) -> None:
        if self.daily_target_g < 0:
            raise ValueError(f"Meta diária de {self.name} não pode ser negativa")
        if not self.reason.strip():
            raise ValueError(f"Justificativa para {self.name} é obrigatória")