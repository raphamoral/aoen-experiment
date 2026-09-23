from typing import List, Optional

from ..domain.entities import RegulatoryFramework
from ..domain.value_objects import ComplianceCategory, RegulatoryBody
from ..infrastructure.repository import RegulatoryFrameworkRepository


class ComplianceCatalogService:
    """
    Application Service do Catálogo de Compliance.

    Gerencia o conhecimento regulatório estruturado da plataforma:
    frameworks, normas, requisitos. Essencial para o matching preciso
    entre projetos de clientes e especialização dos freelancers.
    """

    def __init__(self, repository: RegulatoryFrameworkRepository) -> None:
        self._repository = repository

    async def create_framework(
        self,
        code: str,
        name: str,
        description: str,
        regulatory_body_code: str,
        regulatory_body_name: str,
        country: str,
        category_code: str,
        complexity_level: int,
    ) -> RegulatoryFramework:
        framework = RegulatoryFramework(
            code=code,
            name=name,
            description=description,
            regulatory_body=RegulatoryBody(
                code=regulatory_body_code,
                country=country,
                full_name=regulatory_body_name,
            ),
            category=ComplianceCategory(code=category_code),
            complexity_level=complexity_level,
        )
        await self._repository.save(framework)
        return framework

    async def find_by_code(self, code: str) -> Optional[RegulatoryFramework]:
        return await self._repository.find_by_code(code)

    async def find_by_category(
        self, category_code: str
    ) -> List[RegulatoryFramework]:
        return await self._repository.find_by_category(category_code)

    async def find_all_active(self) -> List[RegulatoryFramework]:
        return await self._repository.find_all_active()

    async def seed_brazilian_frameworks(self) -> None:
        """Popula catálogo com frameworks regulatórios brasileiros prioritários."""
        seeds = [
            {
                "code": "LGPD",
                "name": "Lei Geral de Proteção de Dados",
                "description": "Lei 13.709/2018 — proteção de dados pessoais no Brasil",
                "regulatory_body_code": "ANPD",
                "regulatory_body_name": "Autoridade Nacional de Proteção de Dados",
                "country": "BR",
                "category_code": "DATA_PROTECTION",
                "complexity_level": 3,
            },
            {
                "code": "BACEN_4658",
                "name": "Resolução BACEN 4.658",
                "description": "Política de segurança cibernética para Instituições Financeiras",
                "regulatory_body_code": "BACEN",
                "regulatory_body_name": "Banco Central do Brasil",
                "country": "BR",
                "category_code": "CYBERSECURITY",
                "complexity_level": 4,
            },
            {
                "code": "CVM_598",
                "name": "Resolução CVM 598",
                "description": "Compliance no mercado de capitais brasileiro",
                "regulatory_body_code": "CVM",
                "regulatory_body_name": "Comissão de Valores Mobiliários",
                "country": "BR",
                "category_code": "CAPITAL_MARKETS",
                "complexity_level": 4,
            },
            {
                "code": "COAF_AML",
                "name": "PLD/FT — Prevenção à Lavagem de Dinheiro e Financiamento ao Terrorismo",
                "description": "Normas COAF para PLD-FT — obrigação de todos os setores regulados",
                "regulatory_body_code": "COAF",
                "regulatory_body_name": "Conselho de Controle de Atividades Financeiras",
                "country": "BR",
                "category_code": "ANTI_MONEY_LAUNDERING",
                "complexity_level": 4,
            },
            {
                "code": "SUSEP_CIRCULAR_662",
                "name": "Circular SUSEP 662/2022",
                "description": "Governança corporativa e compliance para seguradoras",
                "regulatory_body_code": "SUSEP",
                "regulatory_body_name": "Superintendência de Seguros Privados",
                "country": "BR",
                "category_code": "CORPORATE_GOVERNANCE",
                "complexity_level": 3,
            },
            {
                "code": "GDPR",
                "name": "General Data Protection Regulation",
                "description": "Regulamento europeu de proteção de dados — impacto em empresas brasileiras com operações na UE",
                "regulatory_body_code": "EDPB",
                "regulatory_body_name": "European Data Protection Board",
                "country": "EU",
                "category_code": "DATA_PROTECTION",
                "complexity_level": 4,
            },
        ]
        for data in seeds:
            existing = await self.find_by_code(data["code"])
            if not existing:
                await self.create_framework(**data)