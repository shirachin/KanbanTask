"""
Task API routes
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import nullslast
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.core.database import get_db
from app.core.db_utils import db_transaction
from app.models import Task, Status, Todo
from app.schemas import TaskCreate, TaskUpdate, TaskResponse, TodoCreate, TodoResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("", response_model=List[TaskResponse])
def get_tasks(
    project_id: Optional[int] = None,
    project_ids: Optional[str] = None,
    assignee: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get tasks with optional filtering"""
    query = db.query(Task)
    
    if project_id is not None:
        query = query.filter(Task.project_id == project_id)
        if assignee:
            query = query.filter(Task.assignee == assignee)
    elif project_ids:
        project_id_list = [int(pid.strip()) for pid in project_ids.split(',') if pid.strip()]
        if project_id_list:
            if -1 in project_id_list:
                other_project_ids = [pid for pid in project_id_list if pid != -1]
                if other_project_ids:
                    if assignee:
                        query = query.filter(
                            ((Task.project_id.in_(other_project_ids)) & (Task.assignee == assignee)) |
                            ((Task.project_id == -1) & (Task.assignee == assignee))
                        )
                    else:
                        query = query.filter(
                            (Task.project_id.in_(other_project_ids)) |
                            (Task.project_id == -1)
                        )
                else:
                    if assignee:
                        query = query.filter((Task.project_id == -1) & (Task.assignee == assignee))
                    else:
                        query = query.filter(Task.project_id == -1)
            else:
                if assignee:
                    query = query.filter(
                        (Task.project_id.in_(project_id_list)) & (Task.assignee == assignee)
                    )
                else:
                    query = query.filter(Task.project_id.in_(project_id_list))
    elif assignee:
        query = query.filter((Task.project_id == -1) & (Task.assignee == assignee))
    
    tasks = query.order_by(
        nullslast(Task.status_id),
        Task.order
    ).offset(skip).limit(limit).all()
    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """Get a single task by ID"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Task with id {task_id} not found")
    return task


@router.post("", response_model=TaskResponse)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """
    Create a new task
    
    Creates a new task. For personal tasks (project_id=-1), assignee is required.
    """
    if task.project_id == -1 and not task.assignee:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Assignee is required for personal tasks")
    
    task_dict = task.dict()
    
    # status_idが指定されていない場合、status名から共通ステータスIDを取得
    if task_dict.get("status_id") is None and task_dict.get("status"):
        status_name = task_dict["status"]
        
        # 共通ステータスを取得（project_id IS NULL）
        status = db.query(Status).filter(
            Status.name == status_name,
            Status.project_id.is_(None)
        ).first()
        if status:
            task_dict["status_id"] = status.id
    
    try:
        with db_transaction(db):
            db_task = Task(**task_dict)
            db.add(db_task)
            db.commit()
            db.refresh(db_task)
            logger.info(f"Task {db_task.id} created successfully")
            return db_task
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating task: {e}", exc_info=True)
        raise


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db)):
    """
    Update a task
    
    Updates an existing task by ID.
    """
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Task with id {task_id} not found")
    
    update_data = task_update.dict(exclude_unset=True)
    
    # status_idが更新される場合の処理
    if "status" in update_data:
        status_name = update_data["status"]
        
        # 共通ステータスを取得（project_id IS NULL）
        status = db.query(Status).filter(
            Status.name == status_name,
            Status.project_id.is_(None)
        ).first()
        if status:
            update_data["status_id"] = status.id
        else:
            # ステータスが見つからない場合はNULL（個人タスクの場合など）
            update_data["status_id"] = None
    
    try:
        with db_transaction(db):
            for field, value in update_data.items():
                setattr(db_task, field, value)
            
            db.commit()
            db.refresh(db_task)
            logger.info(f"Task {task_id} updated successfully")
            return db_task
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {e}", exc_info=True)
        raise


@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """
    Delete a task
    
    Deletes a task by ID. Related todos are also deleted due to cascade.
    """
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Task with id {task_id} not found")
    
    try:
        with db_transaction(db):
            db.delete(db_task)
            db.commit()
            logger.info(f"Task {task_id} deleted successfully")
            return {"message": "Task deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting task {task_id}: {e}", exc_info=True)
        raise


@router.get("/{task_id}/todos", response_model=List[TodoResponse])
def get_task_todos(task_id: int, db: Session = Depends(get_db)):
    """Get todos for a task"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Task with id {task_id} not found")
    
    todos = db.query(Todo).filter(Todo.task_id == task_id).order_by(Todo.order).all()
    return todos


@router.post("/{task_id}/todos", response_model=TodoResponse)
def create_task_todo(task_id: int, todo: TodoCreate, db: Session = Depends(get_db)):
    """
    Create a new todo for a task
    
    Creates a new todo item associated with the specified task.
    """
    from datetime import datetime, date
    
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Task with id {task_id} not found")
    
    todo_dict = todo.dict()
    todo_dict["task_id"] = task_id
    
    # date型をdatetime型に変換
    if "scheduled_date" in todo_dict and todo_dict["scheduled_date"] is not None:
        if isinstance(todo_dict["scheduled_date"], date):
            todo_dict["scheduled_date"] = datetime.combine(todo_dict["scheduled_date"], datetime.min.time())
    if "completed_date" in todo_dict and todo_dict["completed_date"] is not None:
        if isinstance(todo_dict["completed_date"], date):
            todo_dict["completed_date"] = datetime.combine(todo_dict["completed_date"], datetime.min.time())
    
    try:
        with db_transaction(db):
            db_todo = Todo(**todo_dict)
            db.add(db_todo)
            db.commit()
            db.refresh(db_todo)
            logger.info(f"Todo {db_todo.id} created for task {task_id}")
            return db_todo
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating todo for task {task_id}: {e}", exc_info=True)
        raise
