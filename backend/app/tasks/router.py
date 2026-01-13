"""
Tasks router
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.schemas import MessageResponse
from app.tasks import service
from app.tasks.schema import TaskCreate, TaskListQuery, TaskOrderUpdate, TaskResponse, TaskUpdate

router = APIRouter()


@router.get("", response_model=list[TaskResponse])
def get_tasks(
    query_params: TaskListQuery = Depends(),
    db: Session = Depends(get_db),
):
    """Get tasks with optional filtering"""
    try:
        return service.get_tasks(query_params, db)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching tasks: {str(e)}",
        ) from e


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """Get a single task by ID"""
    try:
        return service.get_task(task_id, db)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching task: {str(e)}",
        ) from e


@router.post("", response_model=TaskResponse)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """
    Create a new task

    Creates a new task. For personal tasks (project_id=-1), assignee is required.
    """
    try:
        return service.create_task(task, db)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating task: {str(e)}",
        ) from e


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db)):
    """
    Update a task

    Updates an existing task by ID.
    """
    try:
        return service.update_task(task_id, task_update, db)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating task: {str(e)}",
        ) from e


@router.put("/{task_id}/order", response_model=TaskResponse)
def update_task_order(
    task_id: int,
    order_update: TaskOrderUpdate,
    db: Session = Depends(get_db),
):
    """
    Update task order within the same status

    Updates the order of a task by swapping orders with adjacent tasks.
    The new_index is the index (0-based) in the displayed task list.
    """
    try:
        return service.update_task_order(task_id, order_update, db)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating task order: {str(e)}",
        ) from e


@router.delete("/{task_id}", response_model=MessageResponse)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """
    Delete a task

    Deletes a task by ID. Related todos are also deleted due to cascade.
    """
    try:
        return service.delete_task(task_id, db)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting task: {str(e)}",
        ) from e


