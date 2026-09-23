from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class Issuer:
    name: str
    document: str  # CPF (11 digits) or CNPJ (14 digits)
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Issuer name cannot be empty")
        cleaned = "".join(filter(str.isdigit, self.document))
        if len(cleaned) not in (11, 14):
            raise ValueError("Document must be a valid CPF (11) or CNPJ (14 digits)")
        self.document = cleaned