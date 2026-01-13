from datetime import datetime

from pydantic import BaseModel


class StatusBase(BaseModel):
    name: str
    display_name: str
    order: int = 0
    color: str = "#667eea"
    project_id: int | None = None  # プロジェクトID（共通ステータスの場合はNone）


class StatusCreate(StatusBase):
    pass


class StatusUpdate(BaseModel):
    display_name: str | None = None
    order: int | None = None
    color: str | None = None
    project_id: int | None = None


class StatusResponse(StatusBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class StatusListQuery(BaseModel):
    """Query parameters for listing statuses"""
    project_id: int | None = None

    class Config:
        # Allow query parameters
        from_attributes = True
