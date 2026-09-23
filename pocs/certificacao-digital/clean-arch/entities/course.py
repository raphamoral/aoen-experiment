from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class Course:
    name: str
    description: str
    issuer_id: UUID
    workload_hours: int
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Course name cannot be empty")
        if self.workload_hours <= 0:
            raise ValueError("Workload hours must be a positive integer")