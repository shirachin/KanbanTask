"""
TODO API routes
"""
import logging
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.core.database import get_db
from app.core.db_utils import db_transaction
from app.models import Task, Todo, Project
from app.schemas import TodoUpdate, TodoResponse, TodoListResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("", response_model=TodoListResponse)
def get_all_todos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all todos with pagination
    
    Returns a paginated list of todos with task and project information.
    """
    try:
        query = db.query(Todo).join(Task, Todo.task_id == Task.id).outerjoin(
            Project, Task.project_id == Project.id
        )
        
        total = query.count()
        todos = query.order_by(Todo.order).offset(skip).limit(limit).all()
        
        result = []
        for todo in todos:
            task = todo.task
            project = task.project if task and task.project_id != -1 else None
            result.append({
                "id": todo.id,
                "task_id": todo.task_id,
                "title": todo.title,
                "completed": todo.completed,
                "order": todo.order,
                "scheduled_date": todo.scheduled_date.isoformat() if todo.scheduled_date else None,
                "completed_date": todo.completed_date.isoformat() if todo.completed_date else None,
                "created_at": todo.created_at.isoformat() if todo.created_at else None,
                "updated_at": todo.updated_at.isoformat() if todo.updated_at else None,
                "task_name": task.title if task else None,
                "project_id": task.project_id if task else None,
                "project_name": project.name if project else ("個人タスク" if task and task.project_id == -1 else None),
            })
        
        return TodoListResponse(
            items=result,
            total=total,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        logger.error(f"Error fetching todos: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching todos"
        )


@router.put("/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, todo_update: TodoUpdate, db: Session = Depends(get_db)):
    """
    Update a todo
    
    Updates a todo item. If completed_date is set, completed is automatically set to True.
    """
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if db_todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Todo with id {todo_id} not found")
    
    update_data = todo_update.dict(exclude_unset=True)
    
    # date型をdatetime型に変換
    if "scheduled_date" in update_data and update_data["scheduled_date"] is not None:
        if isinstance(update_data["scheduled_date"], date):
            update_data["scheduled_date"] = datetime.combine(update_data["scheduled_date"], datetime.min.time())
    if "completed_date" in update_data and update_data["completed_date"] is not None:
        if isinstance(update_data["completed_date"], date):
            update_data["completed_date"] = datetime.combine(update_data["completed_date"], datetime.min.time())
    
    # 実行完了日が設定された場合は自動的にcompletedをtrueに、削除された場合はfalseに
    if "completed_date" in update_data:
        if update_data["completed_date"] is not None:
            update_data["completed"] = True
        else:
            update_data["completed"] = False
    
    try:
        with db_transaction(db):
            for field, value in update_data.items():
                setattr(db_todo, field, value)
            
            db.commit()
            db.refresh(db_todo)
            logger.info(f"Todo {todo_id} updated successfully")
            return db_todo
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating todo {todo_id}: {e}", exc_info=True)
        raise


@router.delete("/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    """
    Delete a todo
    
    Deletes a todo item by ID.
    """
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if db_todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Todo with id {todo_id} not found")
    
    try:
        with db_transaction(db):
            db.delete(db_todo)
            db.commit()
            logger.info(f"Todo {todo_id} deleted successfully")
            return {"message": "Todo deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting todo {todo_id}: {e}", exc_info=True)
        raise
