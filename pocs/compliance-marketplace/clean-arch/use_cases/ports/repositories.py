from abc import ABC, abstractmethod
from typing import List, Optional

from entities.freelancer import Freelancer, ComplianceArea
from entities.client import Client
from entities.project import Project, ProjectStatus
from entities.proposal import Proposal
from entities.contract import Contract


class FreelancerRepository(ABC):
    @abstractmethod
    def save(self, freelancer: Freelancer) -> Freelancer: ...

    @abstractmethod
    def find_by_id(self, id: str) -> Optional[Freelancer]: ...

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[Freelancer]: ...

    @abstractmethod
    def find_all(self, specialization: Optional[ComplianceArea] = None) -> List[Freelancer]: ...


class ClientRepository(ABC):
    @abstractmethod
    def save(self, client: Client) -> Client: ...

    @abstractmethod
    def find_by_id(self, id: str) -> Optional[Client]: ...

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[Client]: ...


class ProjectRepository(ABC):
    @abstractmethod
    def save(self, project: Project) -> Project: ...

    @abstractmethod
    def find_by_id(self, id: str) -> Optional[Project]: ...

    @abstractmethod
    def find_by_status(self, status: ProjectStatus) -> List[Project]: ...

    @abstractmethod
    def find_by_compliance_area(
        self, area: ComplianceArea, status: Optional[ProjectStatus] = None
    ) -> List[Project]: ...

    @abstractmethod
    def find_by_client(self, client_id: str) -> List[Project]: ...

    @abstractmethod
    def update(self, project: Project) -> Project: ...


class ProposalRepository(ABC):
    @abstractmethod
    def save(self, proposal: Proposal) -> Proposal: ...

    @abstractmethod
    def find_by_id(self, id: str) -> Optional[Proposal]: ...

    @abstractmethod
    def find_by_project(self, project_id: str) -> List[Proposal]: ...

    @abstractmethod
    def find_by_freelancer(self, freelancer_id: str) -> List[Proposal]: ...

    @abstractmethod
    def find_by_project_and_freelancer(
        self, project_id: str, freelancer_id: str
    ) -> Optional[Proposal]: ...

    @abstractmethod
    def update(self, proposal: Proposal) -> Proposal: ...


class ContractRepository(ABC):
    @abstractmethod
    def save(self, contract: Contract) -> Contract: ...

    @abstractmethod
    def find_by_id(self, id: str) -> Optional[Contract]: ...

    @abstractmethod
    def find_by_project(self, project_id: str) -> Optional[Contract]: ...

    @abstractmethod
    def find_by_freelancer(self, freelancer_id: str) -> List[Contract]: ...

    @abstractmethod
    def update(self, contract: Contract) -> Contract: ...