from datetime import datetime

from pydantic import BaseModel


class ProjectBase(BaseModel):
    name: str
    description: str | None = None
    start_month: str | None = None  # YYYY-MM形式
    end_month: str | None = None  # YYYY-MM形式
    assignee: list[str] | None = None  # 担当者リスト


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    start_month: str | None = None
    end_month: str | None = None
    assignee: list[str] | None = None


class ProjectResponse(ProjectBase):
    id: int
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    """Response model for paginated project list"""

    items: list[ProjectResponse]
    total: int
    skip: int
    limit: int


class ProjectListQuery(BaseModel):
    """Query parameters for listing projects"""
    assignee: str | None = None
    name: str | None = None
    start_month: str | None = None
    end_month: str | None = None
    skip: int = 0
    limit: int = 100
    sort_by: str | None = None
    sort_order: str | None = "desc"

    class Config:
        # Allow query parameters
        from_attributes = True
