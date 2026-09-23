from entities.contract import Contract
from use_cases.ports.repositories import ContractRepository


class GetContract:
    def __init__(self, repository: ContractRepository):
        self.repository = repository

    def execute(self, contract_id: str) -> Contract:
        contract = self.repository.find_by_id(contract_id)
        if not contract:
            raise ValueError(f"Contract '{contract_id}' not found")
        return contract