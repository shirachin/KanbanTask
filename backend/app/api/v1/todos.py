"""
TODO API routes
"""
import logging
from datetime import datetime, date
from typing import Optional
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
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = "asc",
    title: Optional[str] = None,
    completed: Optional[bool] = None,
    task_name: Optional[str] = None,
    project_name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get all todos with pagination, sorting, and filtering
    
    Returns a paginated list of todos with task and project information.
    """
    try:
        query = db.query(Todo).join(Task, Todo.task_id == Task.id).outerjoin(
            Project, Task.project_id == Project.id
        )
        
        # フィルタリング
        if title:
            query = query.filter(Todo.title.ilike(f'%{title}%'))
        if completed is not None:
            query = query.filter(Todo.completed == completed)
        if task_name:
            query = query.filter(Task.title.ilike(f'%{task_name}%'))
        if project_name:
            query = query.filter(Project.name.ilike(f'%{project_name}%'))
        
        # ソート
        sort_column = Todo.order  # デフォルト
        if sort_by:
            if sort_by == "id":
                sort_column = Todo.id
            elif sort_by == "title":
                sort_column = Todo.title
            elif sort_by == "completed":
                sort_column = Todo.completed
            elif sort_by == "order":
                sort_column = Todo.order
            elif sort_by == "scheduled_date":
                sort_column = Todo.scheduled_date
            elif sort_by == "completed_date":
                sort_column = Todo.completed_date
            elif sort_by == "created_at":
                sort_column = Todo.created_at
            elif sort_by == "updated_at":
                sort_column = Todo.updated_at
            elif sort_by == "task_name":
                sort_column = Task.title
            elif sort_by == "project_name":
                sort_column = Project.name
        
        if sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        total = query.count()
        todos = query.offset(skip).limit(limit).all()
        
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
