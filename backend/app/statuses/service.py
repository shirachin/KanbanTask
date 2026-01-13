"""
Statuses service layer
"""
import logging
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.constants import DEFAULT_STATUS_DEFINITIONS
from app.core.db_utils import db_transaction
from app.models import Status
from app.statuses.schema import StatusCreate, StatusListQuery, StatusResponse, StatusUpdate

logger = logging.getLogger(__name__)


def get_statuses(query_params: StatusListQuery, db: Session) -> list[StatusResponse]:
    """Get common statuses (all projects and personal tasks share the same 7 statuses)"""
    # 共通ステータスを取得（project_id IS NULL）
    query = db.query(Status).filter(Status.project_id.is_(None))
    statuses = query.order_by(Status.order).all()

    # 共通ステータスが存在しない場合は、デフォルトステータスを返す（マイグレーション前の互換性のため）
    if not statuses:
        # 仮想的なステータスレスポンスを返す
        return [
            StatusResponse(
                id=idx,
                name=status["name"],
                display_name=status["display_name"],
                order=status["order"],
                color=status["color"],
                project_id=None,
                created_at=datetime.now(),
            )
            for idx, status in enumerate(DEFAULT_STATUS_DEFINITIONS)
        ]

    return statuses


def create_status(status: StatusCreate, db: Session) -> StatusResponse:
    """
    Create a new status

    Creates a new status. Status names must be unique within the same project.
    """
    existing = (
        db.query(Status)
        .filter(Status.name == status.name, Status.project_id == status.project_id)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status with this name already exists in this project",
        )

    with db_transaction(db):
        db_status = Status(**status.dict())
        db.add(db_status)
        db.commit()
        db.refresh(db_status)
    logger.info(f"Status {db_status.id} created successfully")
    return db_status


def update_status(status_id: int, status_update: StatusUpdate, db: Session) -> StatusResponse:
    """
    Update a status

    Updates an existing status by ID.
    """
    db_status = db.query(Status).filter(Status.id == status_id).first()
    if db_status is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Status with id {status_id} not found"
        )

    with db_transaction(db):
        update_data = status_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_status, field, value)

        db.commit()
        db.refresh(db_status)
    logger.info(f"Status {status_id} updated successfully")
    return db_status


def delete_status(status_id: int, db: Session) -> dict:
    """
    Delete a status

    Deletes a status by ID. Cannot delete if there are tasks using this status.
    """
    db_status = db.query(Status).filter(Status.id == status_id).first()
    if db_status is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Status with id {status_id} not found"
        )

    with db_transaction(db):
        db.delete(db_status)
        db.commit()
    logger.info(f"Status {status_id} deleted successfully")
    return {"message": "Status deleted successfully"}
