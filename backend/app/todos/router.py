"""
Todos router
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.schemas import MessageResponse
from app.todos import service
from app.todos.schema import TodoCreate, TodoListQuery, TodoListResponse, TodoResponse, TodoUpdate

router = APIRouter()


@router.get("", response_model=TodoListResponse)
def get_all_todos(
    query_params: TodoListQuery = Depends(),
    db: Session = Depends(get_db),
):
    """
    Get all todos with pagination, sorting, and filtering

    Returns a paginated list of todos with task and project information.
    """
    try:
        return service.get_all_todos(query_params, db)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching todos: {str(e)}",
        ) from e


@router.put("/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, todo_update: TodoUpdate, db: Session = Depends(get_db)):
    """
    Update a todo

    Updates a todo item. If completed_date is set, completed is automatically set to True.
    """
    try:
        return service.update_todo(todo_id, todo_update, db)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating todo: {str(e)}",
        ) from e


@router.delete("/{todo_id}", response_model=MessageResponse)
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    """
    Delete a todo

    Deletes a todo item by ID.
    """
    try:
        return service.delete_todo(todo_id, db)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting todo: {str(e)}",
        ) from e


@router.get("/task/{task_id}", response_model=list[TodoResponse])
def get_task_todos(task_id: int, db: Session = Depends(get_db)):
    """Get todos for a task"""
    try:
        return service.get_task_todos(task_id, db)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching task todos: {str(e)}",
        ) from e


@router.post("/task/{task_id}", response_model=TodoResponse)
def create_task_todo(task_id: int, todo: TodoCreate, db: Session = Depends(get_db)):
    """
    Create a new todo for a task

    Creates a new todo item associated with the specified task.
    """
    try:
        return service.create_task_todo(task_id, todo, db)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating todo: {str(e)}",
        ) from e
