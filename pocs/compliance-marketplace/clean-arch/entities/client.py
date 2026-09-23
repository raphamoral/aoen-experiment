from dataclasses import dataclass, field
import uuid


@dataclass
class Client:
    name: str
    email: str
    company: str
    industry: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    is_active: bool = True

    def __post_init__(self):
        self._validate()

    def _validate(self):
        if not self.name or len(self.name.strip()) < 2:
            raise ValueError("Name must have at least 2 characters")
        if "@" not in self.email or "." not in self.email:
            raise ValueError("Invalid email address")
        if not self.company:
            raise ValueError("Company name is required")
        if not self.industry:
            raise ValueError("Industry is required")