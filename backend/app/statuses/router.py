"""
Statuses router
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.schemas import MessageResponse
from app.statuses import service
from app.statuses.schema import StatusCreate, StatusListQuery, StatusResponse, StatusUpdate

router = APIRouter()


@router.get("", response_model=list[StatusResponse])
def get_statuses(
    query_params: StatusListQuery = Depends(), db: Session = Depends(get_db)
):
    """Get common statuses (all projects and personal tasks share the same 7 statuses)"""
    try:
        return service.get_statuses(query_params, db)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching statuses: {str(e)}",
        ) from e


@router.post("", response_model=StatusResponse)
def create_status(status: StatusCreate, db: Session = Depends(get_db)):
    """
    Create a new status

    Creates a new status. Status names must be unique within the same project.
    """
    try:
        return service.create_status(status, db)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating status: {str(e)}",
        ) from e


@router.put("/{status_id}", response_model=StatusResponse)
def update_status(status_id: int, status_update: StatusUpdate, db: Session = Depends(get_db)):
    """
    Update a status

    Updates an existing status by ID.
    """
    try:
        return service.update_status(status_id, status_update, db)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating status: {str(e)}",
        ) from e


@router.delete("/{status_id}", response_model=MessageResponse)
def delete_status(status_id: int, db: Session = Depends(get_db)):
    """
    Delete a status

    Deletes a status by ID. Cannot delete if there are tasks using this status.
    """
    try:
        return service.delete_status(status_id, db)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting status: {str(e)}",
        ) from e
