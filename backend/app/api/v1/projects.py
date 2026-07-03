import math
import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.common import Page
from app.schemas.project import (
    OrganizationCreate,
    OrganizationResponse,
    ProjectCreate,
    ProjectResponse,
)
from app.services.project_service import ProjectService

router = APIRouter(tags=["Projects"])


@router.post("/organizations", response_model=OrganizationResponse, status_code=201)
def create_organization(
    payload: OrganizationCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    return ProjectService(db).create_organization(user.id, payload)


@router.get("/organizations", response_model=list[OrganizationResponse])
def list_organizations(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return ProjectService(db).list_organizations(user.id)


@router.post("/projects", response_model=ProjectResponse, status_code=201)
def create_project(
    payload: ProjectCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    return ProjectService(db).create_project(payload)


@router.get("/projects/{project_id}", response_model=ProjectResponse)
def get_project(project_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return ProjectService(db).get_project(project_id)


@router.get("/projects", response_model=Page[ProjectResponse])
def list_projects(
    organization_id: uuid.UUID | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    items, total = ProjectService(db).list_projects(
        organization_id, offset=(page - 1) * page_size, limit=page_size
    )
    return Page(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size) if total else 0,
    )
