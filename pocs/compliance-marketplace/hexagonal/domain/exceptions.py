class DomainException(Exception):
    """Raiz de todas as exceções de domínio."""


class FreelancerNotFound(DomainException):
    def __init__(self, freelancer_id):
        super().__init__(f"Freelancer não encontrado: {freelancer_id}")


class ProjectNotFound(DomainException):
    def __init__(self, project_id):
        super().__init__(f"Projeto não encontrado: {project_id}")


class ProposalNotFound(DomainException):
    def __init__(self, proposal_id):
        super().__init__(f"Proposta não encontrada: {proposal_id}")


class IncompatibleExpertise(DomainException):
    """Freelancer não cobre as áreas de compliance exigidas pelo projeto."""


class InvalidProjectTransition(DomainException):
    """Transição de estado inválida no ciclo de vida do projeto."""


class InvalidProposalTransition(DomainException):
    """Transição de estado inválida no ciclo de vida da proposta."""