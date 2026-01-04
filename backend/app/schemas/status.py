from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class StatusBase(BaseModel):
    name: str
    display_name: str
    order: int = 0
    color: str = "#667eea"
    project_id: int  # プロジェクトID

class StatusCreate(StatusBase):
    pass

class StatusUpdate(BaseModel):
    display_name: Optional[str] = None
    order: Optional[int] = None
    color: Optional[str] = None
    project_id: Optional[int] = None

class StatusResponse(StatusBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
