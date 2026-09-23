from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from entities.client import Client
from entities.contract import Contract
from entities.freelancer import Freelancer
from entities.project import Project
from entities.proposal import Proposal
from entities.value_objects import ComplianceSpecialty


class FreelancerRepository(ABC):
    @abstractmethod
    def save(self, freelancer: Freelancer) -> Freelancer: ...

    @abstractmethod
    def find_by_id(self, freelancer_id: UUID) -> Optional[Freelancer]: ...

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[Freelancer]: ...

    @abstractmethod
    def find_by_specialty(self, specialty: ComplianceSpecialty) -> List[Freelancer]: ...

    @abstractmethod
    def list_all(self, skip: int = 0, limit: int = 20) -> List[Freelancer]: ...


class ClientRepository(ABC):
    @abstractmethod
    def save(self, client: Client) -> Client: ...

    @abstractmethod
    def find_by_id(self, client_id: UUID) -> Optional[Client]: ...

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[Client]: ...


class ProjectRepository(ABC):
    @abstractmethod
    def save(self, project: Project) -> Project: ...

    @abstractmethod
    def find_by_id(self, project_id: UUID) -> Optional[Project]: ...

    @abstractmethod
    def list_open(self, skip: int = 0, limit: int = 20) -> List[Project]: ...

    @abstractmethod
    def list_by_client(self, client_id: UUID) -> List[Project]: ...


class ProposalRepository(ABC):
    @abstractmethod
    def save(self, proposal: Proposal) -> Proposal: ...

    @abstractmethod
    def find_by_id(self, proposal_id: UUID) -> Optional[Proposal]: ...

    @abstractmethod
    def find_by_project(self, project_id: UUID) -> List[Proposal]: ...

    @abstractmethod
    def find_by_freelancer(self, freelancer_id: UUID) -> List[Proposal]: ...

    @abstractmethod
    def reject_all_pending_for_project(self, project_id: UUID, except_id: UUID) -> None: ...


class ContractRepository(ABC):
    @abstractmethod
    def save(self, contract: Contract) -> Contract: ...

    @abstractmethod
    def find_by_project(self, project_id: UUID) -> Optional[Contract]: ...

    @abstractmethod
    def find_by_freelancer(self, freelancer_id: UUID) -> List[Contract]: ...