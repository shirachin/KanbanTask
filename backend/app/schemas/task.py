from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "not_started"  # ステータス名を文字列で保存（デフォルトは「未実行」）
    status_id: Optional[int] = None  # ステータスID
    order: int = 0  # 同じステータス内での順序
    completed: bool = False  # 後方互換性のため残す
    project_id: int  # プロジェクトID（-1の場合は個人タスク）
    assignee: Optional[str] = None  # 担当者（個人タスク用、project_id=-1の場合に使用）

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    order: Optional[int] = None
    completed: Optional[bool] = None
    project_id: Optional[int] = None
    assignee: Optional[str] = None

class TaskResponse(TaskBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
