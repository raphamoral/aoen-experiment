from typing import List, Optional

from entities.project import Project, ProjectStatus
from entities.freelancer import ComplianceArea
from use_cases.ports.repositories import ProjectRepository


class ListProjects:
    def __init__(self, repository: ProjectRepository):
        self.repository = repository

    def execute(
        self,
        compliance_area: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Project]:
        try:
            parsed_status = ProjectStatus(status) if status else ProjectStatus.OPEN
        except ValueError:
            raise ValueError(f"Invalid status: '{status}'")

        if compliance_area:
            try:
                parsed_area = ComplianceArea(compliance_area)
            except ValueError:
                raise ValueError(f"Invalid compliance area: '{compliance_area}'")
            return self.repository.find_by_compliance_area(parsed_area, parsed_status)

        return self.repository.find_by_status(parsed_status)