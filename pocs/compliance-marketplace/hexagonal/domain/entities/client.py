from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class Client:
    company_name: str
    email: str
    industry: str
    cnpj: str
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        digits = "".join(filter(str.isdigit, self.cnpj))
        if len(digits) != 14:
            raise ValueError("CNPJ deve conter exatamente 14 dígitos.")
        self.cnpj = digits