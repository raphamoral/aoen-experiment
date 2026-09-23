from fastapi import Depends
from sqlalchemy.orm import Session

from frameworks.database.session import get_db

from adapters.repositories.freelancer_repo import SQLAlchemyFreelancerRepository
from adapters.repositories.client_repo import SQLAlchemyClientRepository
from adapters.repositories.project_repo import SQLAlchemyProjectRepository
from adapters.repositories.proposal_repo import SQLAlchemyProposalRepository
from adapters.repositories.contract_repo import SQLAlchemyContractRepository

from use_cases.freelancer.create_freelancer import CreateFreelancer
from use_cases.freelancer.list_freelancers import ListFreelancers
from use_cases.freelancer.get_freelancer import GetFreelancer
from use_cases.client.create_client import CreateClient
from use_cases.project.post_project import PostProject
from use_cases.project.list_projects import ListProjects
from use_cases.proposal.submit_proposal import SubmitProposal
from use_cases.proposal.accept_proposal import AcceptProposal
from use_cases.proposal.list_proposals import ListProposalsByProject
from use_cases.contract.get_contract import GetContract

from adapters.controllers.freelancer_controller import FreelancerController
from adapters.controllers.client_controller import ClientController
from adapters.controllers.project_controller import ProjectController
from adapters.controllers.proposal_controller import ProposalController


def get_freelancer_controller(db: Session = Depends(get_db)) -> FreelancerController:
    repo = SQLAlchemyFreelancerRepository(db)
    return FreelancerController(
        create_uc=CreateFreelancer(repo),
        list_uc=ListFreelancers(repo),
        get_uc=GetFreelancer(repo),
    )


def get_client_controller(db: Session = Depends(get_db)) -> ClientController:
    repo = SQLAlchemyClientRepository(db)
    return ClientController(create_uc=CreateClient(repo))


def get_project_controller(db: Session = Depends(get_db)) -> ProjectController:
    return ProjectController(
        post_uc=PostProject(
            project_repo=SQLAlchemyProjectRepository(db),
            client_repo=SQLAlchemyClientRepository(db),
        ),
        list_uc=ListProjects(SQLAlchemyProjectRepository(db)),
    )


def get_proposal_controller(db: Session = Depends(get_db)) -> ProposalController:
    proposal_repo = SQLAlchemyProposalRepository(db)
    project_repo = SQLAlchemyProjectRepository(db)
    freelancer_repo = SQLAlchemyFreelancerRepository(db)
    contract_repo = SQLAlchemyContractRepository(db)
    return ProposalController(
        submit_uc=SubmitProposal(proposal_repo, project_repo, freelancer_repo),
        accept_uc=AcceptProposal(proposal_repo, project_repo, contract_repo, SQLAlchemyClientRepository(db)),
        list_uc=ListProposalsByProject(proposal_repo, project_repo),
        get_contract_uc=GetContract(contract_repo),
    )