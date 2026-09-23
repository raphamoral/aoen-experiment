from dataclasses import dataclass


@dataclass(frozen=True)
class Course:
    id: str
    name: str
    duration_hours: int
    description: str
    issuer_name: str