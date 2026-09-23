from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from adapters.controllers.client_controller import ClientController
from adapters.controllers.freelancer_controller import FreelancerController
from adapters.controllers.project_controller import ProjectController
from adapters.controllers.proposal_controller import ProposalController
from adapters.repositories.sqlalchemy_client_repository import SQLAlchemyClientRepository
from adapters.repositories.sqlalchemy_contract_repository import SQLAlchemyContractRepository
from adapters.repositories.sqlalchemy_freelancer_repository import SQLAlchemyFreelancerRepository
from adapters.repositories.sqlalchemy_project_repository import SQLAlchemyProjectRepository
from adapters.repositories.sqlalchemy_proposal_repository import SQLAlchemyProposalRepository
from frameworks.database.connection import get_db_session
from use_cases.accept_proposal import AcceptProposalUseCase
from use_cases.create_project import CreateProjectUseCase
from use_cases.list_projects import ListOpenProjectsUseCase
from use_cases.register_client import RegisterClientUseCase
from use_cases.register_freelancer import RegisterFreelancerUseCase
from use_cases.submit_proposal import SubmitProposalUseCase

DBSession = Annotated[Session, Depends(get_db_session)]


def get_freelancer_controller(session: DBSession) -> FreelancerController:
    repo = SQLAlchemyFreelancerRepository(session)
    return FreelancerController(RegisterFreelancerUseCase(repo))


def get_client_controller(session: DBSession) -> ClientController:
    repo = SQLAlchemyClientRepository(session)
    return ClientController(RegisterClientUseCase(repo))


def get_project_controller(session: DBSession) -> ProjectController:
    project_repo = SQLAlchemyProjectRepository(session)
    client_repo = SQLAlchemyClientRepository(session)
    return ProjectController(
        CreateProjectUseCase(project_repo, client_repo),
        ListOpenProjectsUseCase(project_repo),
    )


def get_proposal_controller(session: DBSession) -> ProposalController:
    proposal_repo = SQLAlchemyProposalRepository(session)
    project_repo = SQLAlchemyProjectRepository(session)
    freelancer_repo = SQLAlchemyFreelancerRepository(session)
    client_repo = SQLAlchemyClientRepository(session)
    contract_repo = SQLAlchemyContractRepository(session)
    return ProposalController(
        SubmitProposalUseCase(proposal_repo, project_repo, freelancer_repo),
        AcceptProposalUseCase(proposal_repo, project_repo, client_repo, contract_repo),
    )