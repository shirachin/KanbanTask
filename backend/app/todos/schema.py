from datetime import date, datetime

from pydantic import BaseModel


class TodoBase(BaseModel):
    title: str
    completed: bool = False
    order: int = 0
    scheduled_date: date | None = None  # 実行予定日
    completed_date: date | None = None  # 実行完了日


class TodoCreate(TodoBase):
    task_id: int


class TodoUpdate(BaseModel):
    title: str | None = None
    completed: bool | None = None
    order: int | None = None
    scheduled_date: date | None = None
    completed_date: date | None = None


class TodoResponse(TodoBase):
    id: int
    task_id: int
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class TodoWithTaskInfo(BaseModel):
    """Todo with task and project information for list view"""

    id: int
    task_id: int
    title: str
    completed: bool
    order: int
    scheduled_date: str | None = None
    completed_date: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    task_name: str | None = None
    project_id: int | None = None
    project_name: str | None = None


class TodoListResponse(BaseModel):
    """Response model for paginated todo list"""

    items: list[TodoWithTaskInfo]
    total: int
    skip: int
    limit: int


class TodoListQuery(BaseModel):
    """Query parameters for listing todos"""
    skip: int = 0
    limit: int = 100
    sort_by: str | None = None
    sort_order: str | None = "asc"
    title: str | None = None
    completed: bool | None = None
    task_name: str | None = None
    project_name: str | None = None

    class Config:
        # Allow query parameters
        from_attributes = True
