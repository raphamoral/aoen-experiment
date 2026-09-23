from enum import Enum


class NutrientLevel(str, Enum):
    DEFICIENT = "deficient"
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    VERY_HIGH = "very_high"