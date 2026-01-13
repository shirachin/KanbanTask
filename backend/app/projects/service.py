"""
Projects service layer
"""
import json
import logging

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.db_utils import db_transaction
from app.models import Project
from app.projects.schema import (
    ProjectCreate,
    ProjectListQuery,
    ProjectListResponse,
    ProjectResponse,
    ProjectUpdate,
)

logger = logging.getLogger(__name__)


def get_projects(query_params: ProjectListQuery, db: Session) -> ProjectListResponse:
    """
    Get projects with pagination, sorting, and filtering
    """
    query = db.query(Project)

    # システム用プロジェクト（id=-1）を除外
    query = query.filter(Project.id != -1)

    # フィルタリング
    if query_params.assignee:
        query = query.filter(Project.assignee.like(f'%"{query_params.assignee}"%'))
    if query_params.name:
        query = query.filter(Project.name.ilike(f"%{query_params.name}%"))
    if query_params.start_month:
        query = query.filter(Project.start_month == query_params.start_month)
    if query_params.end_month:
        query = query.filter(Project.end_month == query_params.end_month)

    # ソート
    sort_column = Project.created_at  # デフォルト
    if query_params.sort_by:
        if query_params.sort_by == "id":
            sort_column = Project.id
        elif query_params.sort_by == "name":
            sort_column = Project.name
        elif query_params.sort_by == "start_month":
            sort_column = Project.start_month
        elif query_params.sort_by == "end_month":
            sort_column = Project.end_month
        elif query_params.sort_by == "created_at":
            sort_column = Project.created_at
        elif query_params.sort_by == "updated_at":
            sort_column = Project.updated_at

    if query_params.sort_order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    # 総件数を取得
    total = query.count()

    # ページネーション
    projects = query.offset(query_params.skip).limit(query_params.limit).all()

    # assigneeをリストに変換
    for project in projects:
        if project.assignee:
            try:
                project.assignee = json.loads(project.assignee)
            except Exception:
                project.assignee = []
        else:
            project.assignee = []

    return ProjectListResponse(
        items=projects, total=total, skip=query_params.skip, limit=query_params.limit
    )


def get_project(project_id: int, db: Session) -> ProjectResponse:
    """Get a single project by ID"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Project with id {project_id} not found"
        )

    # assigneeをリストに変換
    if project.assignee:
        try:
            project.assignee = json.loads(project.assignee)
        except Exception:
            project.assignee = []
    else:
        project.assignee = []

    return project


def create_project(project: ProjectCreate, db: Session) -> ProjectResponse:
    """
    Create a new project

    Creates a new project. Statuses are shared across all projects.
    """
    project_dict = project.dict()

    # assigneeをJSON文字列に変換
    if project_dict.get("assignee") is not None:
        project_dict["assignee"] = json.dumps(project_dict["assignee"], ensure_ascii=False)

    with db_transaction(db):
        db_project = Project(**project_dict)
        db.add(db_project)
        db.flush()

        # ステータスは共通化されているため、プロジェクト作成時にステータスを作成しない

        db.commit()
        db.refresh(db_project)

    # レスポンス用にassigneeをリストに変換
    if db_project.assignee:
        db_project.assignee = json.loads(db_project.assignee)
    else:
        db_project.assignee = []

    logger.info(f"Project {db_project.id} created successfully")
    return db_project


def update_project(project_id: int, project_update: ProjectUpdate, db: Session) -> ProjectResponse:
    """
    Update a project

    Updates an existing project by ID. System project (id=-1) cannot be updated.
    """
    if project_id == -1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Cannot update system project"
        )

    db_project = db.query(Project).filter(Project.id == project_id).first()
    if db_project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Project with id {project_id} not found"
        )

    update_data = project_update.dict(exclude_unset=True)

    if "assignee" in update_data and update_data["assignee"] is not None:
        update_data["assignee"] = json.dumps(update_data["assignee"], ensure_ascii=False)

    with db_transaction(db):
        for field, value in update_data.items():
            setattr(db_project, field, value)

        db.commit()
        db.refresh(db_project)

    # レスポンス用にassigneeをリストに変換
    if db_project.assignee:
        try:
            db_project.assignee = json.loads(db_project.assignee)
        except Exception:
            db_project.assignee = []
    else:
        db_project.assignee = []

    logger.info(f"Project {project_id} updated successfully")
    return db_project


def delete_project(project_id: int, db: Session) -> dict:
    """
    Delete a project

    Deletes a project by ID. System project (id=-1) cannot be deleted.
    Related tasks are also deleted due to cascade.
    """
    if project_id == -1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Cannot delete system project"
        )

    db_project = db.query(Project).filter(Project.id == project_id).first()
    if db_project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Project with id {project_id} not found"
        )

    with db_transaction(db):
        db.delete(db_project)
        db.commit()
    logger.info(f"Project {project_id} deleted successfully")
    return {"message": "Project deleted successfully"}
