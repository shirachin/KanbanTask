"""
API v1 routes
"""
from fastapi import APIRouter

from app.api.v1 import tasks, projects, statuses, todos

api_router = APIRouter()

api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(statuses.router, prefix="/statuses", tags=["statuses"])
api_router.include_router(todos.router, prefix="/todos", tags=["todos"])
