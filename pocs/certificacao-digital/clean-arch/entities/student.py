import re
from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class Student:
    name: str
    email: str
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Student name cannot be empty")
        if not self._is_valid_email(self.email):
            raise ValueError(f"Invalid email address: {self.email}")

    @staticmethod
    def _is_valid_email(email: str) -> bool:
        return bool(re.match(r"^[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}$", email))