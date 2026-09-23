from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class Patient:
    name: str
    email: str
    age: int
    gender: str  # "M" or "F"
    health_goals: list[str]
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        if not 0 < self.age < 150:
            raise ValueError(f"Invalid age: {self.age}")
        if self.gender not in ("M", "F"):
            raise ValueError("Gender must be 'M' or 'F'")
        if "@" not in self.email:
            raise ValueError(f"Invalid email: {self.email}")
        if not self.name.strip():
            raise ValueError("Name cannot be empty")