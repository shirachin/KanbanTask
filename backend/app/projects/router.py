"""
Projects router
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.schemas import MessageResponse
from app.projects import service
from app.projects.schema import (
    ProjectCreate,
    ProjectListQuery,
    ProjectListResponse,
    ProjectResponse,
    ProjectUpdate,
)

router = APIRouter()


@router.get("", response_model=ProjectListResponse)
def get_projects(
    query_params: ProjectListQuery = Depends(),
    db: Session = Depends(get_db),
):
    """
    Get projects with pagination, sorting, and filtering

    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return
    - **sort_by**: Column to sort by (default: created_at)
    - **sort_order**: Sort order (asc or desc, default: desc)
    - **assignee**: Filter by assignee name
    - **name**: Filter by project name (partial match)
    - **start_month**: Filter by start month (exact match)
    - **end_month**: Filter by end month (exact match)
    """
    try:
        return service.get_projects(query_params, db)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching projects: {str(e)}",
        ) from e


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    """Get a single project by ID"""
    try:
        return service.get_project(project_id, db)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching project: {str(e)}",
        ) from e


@router.post("", response_model=ProjectResponse)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    """
    Create a new project

    Creates a new project. Statuses are shared across all projects.
    """
    try:
        return service.create_project(project, db)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating project: {str(e)}",
        ) from e


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: int, project_update: ProjectUpdate, db: Session = Depends(get_db)):
    """
    Update a project

    Updates an existing project by ID. System project (id=-1) cannot be updated.
    """
    try:
        return service.update_project(project_id, project_update, db)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating project: {str(e)}",
        ) from e


@router.delete("/{project_id}", response_model=MessageResponse)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    """
    Delete a project

    Deletes a project by ID. System project (id=-1) cannot be deleted.
    Related tasks are also deleted due to cascade.
    """
    try:
        return service.delete_project(project_id, db)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting project: {str(e)}",
        ) from e
