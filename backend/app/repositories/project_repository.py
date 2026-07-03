from app.models.organization import Organization
from app.models.project import Project
from app.repositories.base import BaseRepository


class OrganizationRepository(BaseRepository[Organization]):
    model = Organization


class ProjectRepository(BaseRepository[Project]):
    model = Project
