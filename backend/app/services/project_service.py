import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.organization import Organization
from app.models.project import Project
from app.repositories.project_repository import OrganizationRepository, ProjectRepository
from app.schemas.project import OrganizationCreate, ProjectCreate


class ProjectService:
    def __init__(self, db: Session):
        self.db = db
        self.orgs = OrganizationRepository(db)
        self.projects = ProjectRepository(db)

    def create_organization(self, owner_id: uuid.UUID, data: OrganizationCreate) -> Organization:
        org = Organization(name=data.name, owner_id=owner_id)
        self.orgs.add(org)
        self.db.commit()
        self.db.refresh(org)
        return org

    def list_organizations(self, owner_id: uuid.UUID) -> list[Organization]:
        items, _ = self.orgs.list(limit=100, owner_id=owner_id)
        return items

    def create_project(self, data: ProjectCreate) -> Project:
        if not self.orgs.get(data.organization_id):
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Organization not found")
        project = Project(organization_id=data.organization_id, name=data.name, description=data.description)
        self.projects.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def get_project(self, project_id: uuid.UUID) -> Project:
        project = self.projects.get(project_id)
        if not project:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Project not found")
        return project

    def list_projects(self, organization_id: uuid.UUID | None, offset: int, limit: int):
        return self.projects.list(offset=offset, limit=limit, organization_id=organization_id)
