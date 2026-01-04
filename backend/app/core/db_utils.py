"""
Database utility functions for error handling
"""
from contextlib import contextmanager
from typing import Generator
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)


@contextmanager
def db_transaction(db: Session) -> Generator[None, None, None]:
    """
    Context manager for database transactions with automatic rollback on error
    
    Usage:
        with db_transaction(db):
            db.add(item)
            db.commit()
    """
    try:
        yield
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error in transaction: {e}")
        error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
        
        # ユーザーフレンドリーなメッセージに変換
        if "foreign key constraint" in error_msg.lower() or "FOREIGN KEY" in error_msg:
            detail = "Cannot perform this operation due to related data constraints"
        elif "unique constraint" in error_msg.lower() or "UNIQUE" in error_msg:
            detail = "A record with this value already exists"
        elif "not null constraint" in error_msg.lower() or "NOT NULL" in error_msg:
            detail = "Required field is missing"
        else:
            detail = "Database constraint violation"
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error in transaction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error in transaction: {e}")
        raise
