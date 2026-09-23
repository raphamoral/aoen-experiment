from datetime import datetime
from typing import List, Optional

from shared.events.bus import event_bus
from ..domain.entities import Contract
from ..domain.value_objects import ContractPeriod, ContractValue, DeliverableScope
from ..infrastructure.repository import ContractRepository


class ContractingService:
    """
    Application Service de Contratação.

    Orquestra o ciclo de vida do contrato: criação, escopo,
    assinatura digital e conclusão (que dispara liberação do pagamento).
    """

    def __init__(self, repository: ContractRepository) -> None:
        self._repository = repository

    async def create_contract(
        self,
        client_id: str,
        freelancer_id: str,
        match_id: str,
        amount_brl: float,
        start_date: datetime,
        end_date: datetime,
    ) -> Contract:
        contract = Contract.create(
            client_id=client_id,
            freelancer_id=freelancer_id,
            match_id=match_id,
            value=ContractValue(amount=amount_brl),
            period=ContractPeriod(start_date=start_date, end_date=end_date),
        )
        await self._repository.save(contract)
        for event in contract.collect_domain_events():
            await event_bus.publish(event)
        return contract

    async def add_deliverable(
        self,
        contract_id: str,
        title: str,
        description: str,
        estimated_hours: int,
        framework_code: str,
    ) -> Contract:
        contract = await self._get_or_raise(contract_id)
        contract.add_deliverable(
            DeliverableScope(
                title=title,
                description=description,
                estimated_hours=estimated_hours,
                framework_code=framework_code,
            )
        )
        await self._repository.save(contract)
        return contract

    async def submit_for_signature(self, contract_id: str) -> Contract:
        contract = await self._get_or_raise(contract_id)
        contract.submit_for_signature()
        await self._repository.save(contract)
        return contract

    async def sign_contract(self, contract_id: str, signer_role: str) -> Contract:
        contract = await self._get_or_raise(contract_id)
        if signer_role == "client":
            contract.sign_as_client()
        elif signer_role == "freelancer":
            contract.sign_as_freelancer()
        else:
            raise ValueError(f"Papel de assinatura inválido: '{signer_role}'")
        await self._repository.save(contract)
        for event in contract.collect_domain_events():
            await event_bus.publish(event)
        return contract

    async def complete_contract(self, contract_id: str) -> Contract:
        contract = await self._get_or_raise(contract_id)
        contract.complete()
        await self._repository.save(contract)
        for event in contract.collect_domain_events():
            await event_bus.publish(event)
        return contract

    async def find_by_id(self, contract_id: str) -> Optional[Contract]:
        return await self._repository.find_by_id(contract_id)

    async def find_by_client(self, client_id: str) -> List[Contract]:
        return await self._repository.find_by_client(client_id)

    async def _get_or_raise(self, contract_id: str) -> Contract:
        contract = await self._repository.find_by_id(contract_id)
        if not contract:
            raise ValueError(f"Contrato '{contract_id}' não encontrado")
        return contract