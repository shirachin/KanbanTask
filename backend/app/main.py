"""
FastAPI application entry point
"""
from fastapi import FastAPI

from app.core.config import settings
from app.core.middleware import setup_cors
from app.core.exceptions import (
    validation_exception_handler,
    global_exception_handler
)
from app.core.startup import startup_event
from app.api.v1 import api_router
from fastapi.exceptions import RequestValidationError

app = FastAPI(title="Task Management API")

# Setup middleware
setup_cors(app)

# Setup exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Startup event
@app.on_event("startup")
def on_startup():
    startup_event()


@app.get("/")
def read_root():
    return {"message": "Task Management API"}
