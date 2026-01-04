"""
Status API routes
"""
import logging
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.core.database import get_db
from app.models import Status
from app.schemas import StatusCreate, StatusUpdate, StatusResponse
from app.core.constants import DEFAULT_PERSONAL_STATUSES

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("", response_model=List[StatusResponse])
def get_statuses(project_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Get statuses for a project"""
    try:
        if project_id == -1:
            # 個人タスク用のデフォルトステータス
            personal_statuses = [
                {**status, "created_at": datetime.now()}
                for status in DEFAULT_PERSONAL_STATUSES
            ]
            return [StatusResponse(**status) for status in personal_statuses]
        
        query = db.query(Status)
        if project_id is not None:
            query = query.filter(Status.project_id == project_id)
        statuses = query.order_by(Status.order).all()
        return statuses
    except Exception as e:
        logger.error(f"Error fetching statuses: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error fetching statuses")


@router.post("", response_model=StatusResponse)
def create_status(status: StatusCreate, db: Session = Depends(get_db)):
    """Create a new status"""
    existing = db.query(Status).filter(
        Status.name == status.name,
        Status.project_id == status.project_id
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Status with this name already exists in this project")
    
    try:
        db_status = Status(**status.dict())
        db.add(db_status)
        db.commit()
        db.refresh(db_status)
        return db_status
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create status due to database constraints"
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )
    except Exception as e:
        db.rollback()
        raise


@router.put("/{status_id}", response_model=StatusResponse)
def update_status(status_id: int, status_update: StatusUpdate, db: Session = Depends(get_db)):
    """Update a status"""
    db_status = db.query(Status).filter(Status.id == status_id).first()
    if db_status is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Status with id {status_id} not found")
    
    try:
        update_data = status_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_status, field, value)
        
        db.commit()
        db.refresh(db_status)
        return db_status
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update status due to database constraints"
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )
    except Exception as e:
        db.rollback()
        raise


@router.delete("/{status_id}")
def delete_status(status_id: int, db: Session = Depends(get_db)):
    """Delete a status"""
    db_status = db.query(Status).filter(Status.id == status_id).first()
    if db_status is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Status with id {status_id} not found")
    
    try:
        db.delete(db_status)
        db.commit()
        return {"message": "Status deleted successfully"}
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete status due to related data constraints"
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )
    except Exception as e:
        db.rollback()
        raise
