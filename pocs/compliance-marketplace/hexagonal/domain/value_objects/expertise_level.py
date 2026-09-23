from enum import Enum


class ExpertiseLevel(str, Enum):
    JUNIOR = "JUNIOR"
    PLENO = "PLENO"
    SENIOR = "SENIOR"
    SPECIALIST = "SPECIALIST"