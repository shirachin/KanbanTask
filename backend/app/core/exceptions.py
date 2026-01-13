"""
Exception handlers
"""

import logging
import traceback

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

logger = logging.getLogger(__name__)


def get_cors_headers():
    """Get CORS headers"""
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "*",
    }


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
        headers=get_cors_headers(),
    )


async def global_exception_handler(request: Request, exc: Exception):
    """Handle all exceptions"""
    error_trace = traceback.format_exc()
    logger.error(f"Unhandled exception: {exc}")
    logger.error(f"Traceback: {error_trace}")

    from fastapi import HTTPException

    # HTTPExceptionの場合はそのまま返す
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code, content={"detail": exc.detail}, headers=get_cors_headers()
        )

    # IntegrityError（外部キー制約違反、ユニーク制約違反など）
    if isinstance(exc, IntegrityError):
        logger.error(f"Integrity error: {exc}")
        error_msg = str(exc.orig) if hasattr(exc, "orig") else str(exc)

        # ユーザーフレンドリーなメッセージに変換
        if "foreign key constraint" in error_msg.lower() or "FOREIGN KEY" in error_msg:
            detail = "Cannot perform this operation due to related data constraints"
        elif "unique constraint" in error_msg.lower() or "UNIQUE" in error_msg:
            detail = "A record with this value already exists"
        elif "not null constraint" in error_msg.lower() or "NOT NULL" in error_msg:
            detail = "Required field is missing"
        else:
            detail = "Database constraint violation"

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": detail},
            headers=get_cors_headers(),
        )

    # その他のSQLAlchemyエラーの場合
    if isinstance(exc, SQLAlchemyError):
        logger.error(f"Database error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Database error occurred"},
            headers=get_cors_headers(),
        )

    # その他の例外は500エラーとして返す
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
        headers=get_cors_headers(),
    )
