"""
FastAPI application entry point
"""

from fastapi import APIRouter, FastAPI
from fastapi.exceptions import RequestValidationError

from app.core.exceptions import global_exception_handler, validation_exception_handler
from app.core.middleware import setup_cors
from app.core.startup import startup_event
from app.projects import router as projects_router
from app.statuses import router as statuses_router
from app.tasks import router as tasks_router
from app.todos import router as todos_router

app = FastAPI(title="Task Management API")

# Setup middleware
setup_cors(app)

# Setup exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Include API routes
api_router = APIRouter()
api_router.include_router(tasks_router, prefix="/tasks", tags=["tasks"])
api_router.include_router(projects_router, prefix="/projects", tags=["projects"])
api_router.include_router(statuses_router, prefix="/statuses", tags=["statuses"])
api_router.include_router(todos_router, prefix="/todos", tags=["todos"])
app.include_router(api_router, prefix="/api/v1")


# Startup event
@app.on_event("startup")
def on_startup():
    startup_event()


@app.get("/")
def read_root():
    return {"message": "Task Management API"}
