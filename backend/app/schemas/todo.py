from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional

class TodoBase(BaseModel):
    title: str
    completed: bool = False
    order: int = 0
    scheduled_date: Optional[date] = None  # 実行予定日
    completed_date: Optional[date] = None  # 実行完了日

class TodoCreate(TodoBase):
    task_id: int

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    completed: Optional[bool] = None
    order: Optional[int] = None
    scheduled_date: Optional[date] = None
    completed_date: Optional[date] = None

class TodoResponse(TodoBase):
    id: int
    task_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TodoWithTaskInfo(BaseModel):
    """Todo with task and project information for list view"""
    id: int
    task_id: int
    title: str
    completed: bool
    order: int
    scheduled_date: Optional[str] = None
    completed_date: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    task_name: Optional[str] = None
    project_id: Optional[int] = None
    project_name: Optional[str] = None


class TodoListResponse(BaseModel):
    """Response model for paginated todo list"""
    items: list[TodoWithTaskInfo]
    total: int
    skip: int
    limit: int
