from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_month: Optional[str] = None  # YYYY-MM形式
    end_month: Optional[str] = None  # YYYY-MM形式
    assignee: Optional[List[str]] = None  # 担当者リスト

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_month: Optional[str] = None
    end_month: Optional[str] = None
    assignee: Optional[List[str]] = None

class ProjectResponse(ProjectBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    """Response model for paginated project list"""
    items: List[ProjectResponse]
    total: int
    skip: int
    limit: int
