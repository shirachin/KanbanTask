"""
Todos service layer
"""
import logging
from datetime import date, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.db_utils import db_transaction
from app.models import Project, Task, Todo
from app.todos.schema import TodoCreate, TodoListQuery, TodoListResponse, TodoResponse, TodoUpdate

logger = logging.getLogger(__name__)


def get_all_todos(query_params: TodoListQuery, db: Session) -> TodoListResponse:
    """
    Get all todos with pagination, sorting, and filtering

    Returns a paginated list of todos with task and project information.
    """
    query = (
        db.query(Todo)
        .join(Task, Todo.task_id == Task.id)
        .outerjoin(Project, Task.project_id == Project.id)
    )

    # フィルタリング
    if query_params.title:
        query = query.filter(Todo.title.ilike(f"%{query_params.title}%"))
    if query_params.completed is not None:
        query = query.filter(Todo.completed == query_params.completed)
    if query_params.task_name:
        query = query.filter(Task.title.ilike(f"%{query_params.task_name}%"))
    if query_params.project_name:
        query = query.filter(Project.name.ilike(f"%{query_params.project_name}%"))

    # ソート
    sort_column = Todo.order  # デフォルト
    if query_params.sort_by:
        if query_params.sort_by == "id":
            sort_column = Todo.id
        elif query_params.sort_by == "title":
            sort_column = Todo.title
        elif query_params.sort_by == "completed":
            sort_column = Todo.completed
        elif query_params.sort_by == "order":
            sort_column = Todo.order
        elif query_params.sort_by == "scheduled_date":
            sort_column = Todo.scheduled_date
        elif query_params.sort_by == "completed_date":
            sort_column = Todo.completed_date
        elif query_params.sort_by == "created_at":
            sort_column = Todo.created_at
        elif query_params.sort_by == "updated_at":
            sort_column = Todo.updated_at
        elif query_params.sort_by == "task_name":
            sort_column = Task.title
        elif query_params.sort_by == "project_name":
            sort_column = Project.name

    if query_params.sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    total = query.count()
    todos = query.offset(query_params.skip).limit(query_params.limit).all()

    result = []
    for todo in todos:
        task = todo.task
        project = task.project if task and task.project_id != -1 else None
        result.append(
            {
                "id": todo.id,
                "task_id": todo.task_id,
                "title": todo.title,
                "completed": todo.completed,
                "order": todo.order,
                "scheduled_date": todo.scheduled_date.isoformat()
                if todo.scheduled_date
                else None,
                "completed_date": todo.completed_date.isoformat()
                if todo.completed_date
                else None,
                "created_at": todo.created_at.isoformat() if todo.created_at else None,
                "updated_at": todo.updated_at.isoformat() if todo.updated_at else None,
                "task_name": task.title if task else None,
                "project_id": task.project_id if task else None,
                "project_name": project.name
                if project
                else ("個人タスク" if task and task.project_id == -1 else None),
            }
        )

    return TodoListResponse(
        items=result, total=total, skip=query_params.skip, limit=query_params.limit
    )


def update_todo(todo_id: int, todo_update: TodoUpdate, db: Session) -> TodoResponse:
    """
    Update a todo

    Updates a todo item. If completed_date is set, completed is automatically set to True.
    """
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if db_todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Todo with id {todo_id} not found"
        )

    update_data = todo_update.dict(exclude_unset=True)

    # date型をdatetime型に変換
    if "scheduled_date" in update_data and update_data["scheduled_date"] is not None:
        if isinstance(update_data["scheduled_date"], date):
            update_data["scheduled_date"] = datetime.combine(
                update_data["scheduled_date"], datetime.min.time()
            )
    if "completed_date" in update_data and update_data["completed_date"] is not None:
        if isinstance(update_data["completed_date"], date):
            update_data["completed_date"] = datetime.combine(
                update_data["completed_date"], datetime.min.time()
            )

    # 実行完了日が設定された場合は自動的にcompletedをtrueに、削除された場合はfalseに
    if "completed_date" in update_data:
        if update_data["completed_date"] is not None:
            update_data["completed"] = True
        else:
            update_data["completed"] = False

    with db_transaction(db):
        for field, value in update_data.items():
            setattr(db_todo, field, value)

        db.commit()
        db.refresh(db_todo)
    logger.info(f"Todo {todo_id} updated successfully")
    return db_todo


def delete_todo(todo_id: int, db: Session) -> dict:
    """
    Delete a todo

    Deletes a todo item by ID.
    """
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if db_todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Todo with id {todo_id} not found"
        )

    with db_transaction(db):
        db.delete(db_todo)
        db.commit()
    logger.info(f"Todo {todo_id} deleted successfully")
    return {"message": "Todo deleted successfully"}


def get_task_todos(task_id: int, db: Session) -> list[TodoResponse]:
    """Get todos for a task"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Task with id {task_id} not found"
        )

    todos = db.query(Todo).filter(Todo.task_id == task_id).order_by(Todo.order).all()
    return todos


def create_task_todo(task_id: int, todo: TodoCreate, db: Session) -> TodoResponse:
    """
    Create a new todo for a task

    Creates a new todo item associated with the specified task.
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Task with id {task_id} not found"
        )

    todo_dict = todo.dict()
    todo_dict["task_id"] = task_id

    # date型をdatetime型に変換
    if "scheduled_date" in todo_dict and todo_dict["scheduled_date"] is not None:
        if isinstance(todo_dict["scheduled_date"], date):
            todo_dict["scheduled_date"] = datetime.combine(
                todo_dict["scheduled_date"], datetime.min.time()
            )
    if "completed_date" in todo_dict and todo_dict["completed_date"] is not None:
        if isinstance(todo_dict["completed_date"], date):
            todo_dict["completed_date"] = datetime.combine(
                todo_dict["completed_date"], datetime.min.time()
            )

    with db_transaction(db):
        db_todo = Todo(**todo_dict)
        db.add(db_todo)
        db.commit()
        db.refresh(db_todo)
    logger.info(f"Todo {db_todo.id} created for task {task_id}")
    return db_todo
