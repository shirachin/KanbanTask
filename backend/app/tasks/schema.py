from datetime import datetime

from pydantic import BaseModel


class TaskBase(BaseModel):
    title: str
    description: str | None = None
    status: str = "not_started"  # ステータス名を文字列で保存（デフォルトは「未実行」）
    status_id: int | None = None  # ステータスID
    order: int = 0  # 同じステータス内での順序
    completed: bool = False  # 後方互換性のため残す
    project_id: int  # プロジェクトID（-1の場合は個人タスク）
    assignee: str | None = None  # 担当者（個人タスク用、project_id=-1の場合に使用）


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None
    order: int | None = None
    completed: bool | None = None
    project_id: int | None = None
    assignee: str | None = None


class TaskResponse(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class TaskOrderUpdate(BaseModel):
    """Request schema for updating task order"""
    new_index: int


class TaskListQuery(BaseModel):
    """Query parameters for listing tasks"""
    project_id: int | None = None
    project_ids: str | None = None
    assignee: str | None = None
    skip: int = 0
    limit: int = 100

    class Config:
        # Allow query parameters
        from_attributes = True
