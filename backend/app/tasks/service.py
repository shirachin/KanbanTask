"""
Tasks service layer
"""
import logging

from fastapi import HTTPException, status
from sqlalchemy import nullslast
from sqlalchemy.orm import Session

from app.core.db_utils import db_transaction
from app.models import Status, Task
from app.tasks.schema import TaskCreate, TaskListQuery, TaskOrderUpdate, TaskResponse, TaskUpdate

logger = logging.getLogger(__name__)


def get_tasks(query_params: TaskListQuery, db: Session) -> list[TaskResponse]:
    """Get tasks with optional filtering"""
    query = db.query(Task)

    if query_params.project_id is not None:
        query = query.filter(Task.project_id == query_params.project_id)
        if query_params.assignee:
            query = query.filter(Task.assignee == query_params.assignee)
    elif query_params.project_ids:
        project_id_list = [
            int(pid.strip()) for pid in query_params.project_ids.split(",") if pid.strip()
        ]
        if project_id_list:
            if -1 in project_id_list:
                other_project_ids = [pid for pid in project_id_list if pid != -1]
                if other_project_ids:
                    if query_params.assignee:
                        query = query.filter(
                            ((Task.project_id.in_(other_project_ids)) & (Task.assignee == query_params.assignee))
                            | ((Task.project_id == -1) & (Task.assignee == query_params.assignee))
                        )
                    else:
                        query = query.filter(
                            (Task.project_id.in_(other_project_ids)) | (Task.project_id == -1)
                        )
                else:
                    if query_params.assignee:
                        query = query.filter((Task.project_id == -1) & (Task.assignee == query_params.assignee))
                    else:
                        query = query.filter(Task.project_id == -1)
            else:
                if query_params.assignee:
                    query = query.filter(
                        (Task.project_id.in_(project_id_list)) & (Task.assignee == query_params.assignee)
                    )
                else:
                    query = query.filter(Task.project_id.in_(project_id_list))
    elif query_params.assignee:
        query = query.filter((Task.project_id == -1) & (Task.assignee == query_params.assignee))

    tasks = (
        query.order_by(nullslast(Task.status_id), Task.order)
        .offset(query_params.skip)
        .limit(query_params.limit)
        .all()
    )
    return tasks


def get_task(task_id: int, db: Session) -> TaskResponse:
    """Get a single task by ID"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Task with id {task_id} not found"
        )
    return task


def create_task(task: TaskCreate, db: Session) -> TaskResponse:
    """
    Create a new task

    Creates a new task. For personal tasks (project_id=-1), assignee is required.
    """
    if task.project_id == -1 and not task.assignee:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assignee is required for personal tasks",
        )

    task_dict = task.dict()

    # status_idが指定されていない場合、status名から共通ステータスIDを取得
    if task_dict.get("status_id") is None and task_dict.get("status"):
        status_name = task_dict["status"]

        # 共通ステータスを取得（project_id IS NULL）
        status_obj = (
            db.query(Status).filter(Status.name == status_name, Status.project_id.is_(None)).first()
        )
        if status_obj:
            task_dict["status_id"] = status_obj.id

    with db_transaction(db):
        db_task = Task(**task_dict)
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
    logger.info(f"Task {db_task.id} created successfully")
    return db_task


def update_task(task_id: int, task_update: TaskUpdate, db: Session) -> TaskResponse:
    """
    Update a task

    Updates an existing task by ID.
    """
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if db_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Task with id {task_id} not found"
        )

    update_data = task_update.dict(exclude_unset=True)

    # status_idが更新される場合の処理
    if "status" in update_data:
        status_name = update_data["status"]

        # 共通ステータスを取得（project_id IS NULL）
        status_obj = (
            db.query(Status).filter(Status.name == status_name, Status.project_id.is_(None)).first()
        )
        if status_obj:
            update_data["status_id"] = status_obj.id
        else:
            # ステータスが見つからない場合はNULL（個人タスクの場合など）
            update_data["status_id"] = None

    with db_transaction(db):
        for field, value in update_data.items():
            setattr(db_task, field, value)

        db.commit()
        db.refresh(db_task)
    logger.info(f"Task {task_id} updated successfully")
    return db_task


def update_task_order(task_id: int, order_update: TaskOrderUpdate, db: Session) -> TaskResponse:
    """
    Update task order within the same status

    Updates the order of a task by swapping orders with adjacent tasks.
    The new_index is the index (0-based) in the displayed task list.
    """
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if db_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Task with id {task_id} not found"
        )

    with db_transaction(db):
        # 同じステータス内のすべてのタスクを取得（orderでソート）
        status_id = db_task.status_id
        if status_id is None:
            # status_idがnullの場合は、status名でフィルタリング
            same_status_tasks = (
                db.query(Task).filter(Task.status == db_task.status).order_by(Task.order).all()
            )
        else:
            same_status_tasks = (
                db.query(Task).filter(Task.status_id == status_id).order_by(Task.order).all()
            )

        # 移動したタスクを含むすべてのタスクをorderでソート
        all_tasks = sorted(same_status_tasks, key=lambda t: t.order or 0)

        # 移動したタスクの現在のインデックスを取得
        old_index = next((i for i, t in enumerate(all_tasks) if t.id == task_id), None)
        if old_index is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found in status",
            )

        # 新しいインデックスが範囲外の場合は調整
        new_index = order_update.new_index
        if new_index < 0:
            new_index = 0
        if new_index >= len(all_tasks):
            new_index = len(all_tasks) - 1

        # 同じ位置の場合は何もしない
        if old_index == new_index:
            db.commit()
            db.refresh(db_task)
            return db_task

        # 移動したタスクの現在のorder
        task_order = db_task.order or 0

        # 新しい位置のタスクのorderを取得
        target_task = all_tasks[new_index]
        target_order = target_task.order or 0

        # orderを入れ替える
        db_task.order = target_order
        target_task.order = task_order

        db.commit()
        db.refresh(db_task)
    logger.info(f"Task {task_id} order swapped: moved from index {old_index} to {new_index}")
    return db_task


def delete_task(task_id: int, db: Session) -> dict:
    """
    Delete a task

    Deletes a task by ID. Related todos are also deleted due to cascade.
    """
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if db_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Task with id {task_id} not found"
        )

    with db_transaction(db):
        db.delete(db_task)
        db.commit()
    logger.info(f"Task {task_id} deleted successfully")
    return {"message": "Task deleted successfully"}


