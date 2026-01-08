"""
Project API routes
"""
import json
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.core.database import get_db
from app.core.db_utils import db_transaction
from app.models import Project, Status
from app.schemas import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectListResponse
from app.core.constants import DEFAULT_STATUS_DEFINITIONS

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("", response_model=ProjectListResponse)
def get_projects(
    assignee: Optional[str] = None,
    name: Optional[str] = None,
    start_month: Optional[str] = None,
    end_month: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = "desc",
    db: Session = Depends(get_db)
):
    """
    Get projects with pagination, sorting, and filtering
    
    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return
    - **sort_by**: Column to sort by (default: created_at)
    - **sort_order**: Sort order (asc or desc, default: desc)
    - **assignee**: Filter by assignee name
    - **name**: Filter by project name (partial match)
    - **start_month**: Filter by start month (exact match)
    - **end_month**: Filter by end month (exact match)
    """
    try:
        query = db.query(Project)
        
        # システム用プロジェクト（id=-1）を除外
        query = query.filter(Project.id != -1)
        
        # フィルタリング
        if assignee:
            query = query.filter(Project.assignee.like(f'%"{assignee}"%'))
        if name:
            query = query.filter(Project.name.ilike(f'%{name}%'))
        if start_month:
            query = query.filter(Project.start_month == start_month)
        if end_month:
            query = query.filter(Project.end_month == end_month)
        
        # ソート
        sort_column = Project.created_at  # デフォルト
        if sort_by:
            if sort_by == "id":
                sort_column = Project.id
            elif sort_by == "name":
                sort_column = Project.name
            elif sort_by == "start_month":
                sort_column = Project.start_month
            elif sort_by == "end_month":
                sort_column = Project.end_month
            elif sort_by == "created_at":
                sort_column = Project.created_at
            elif sort_by == "updated_at":
                sort_column = Project.updated_at
        
        if sort_order == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())
        
        # 総件数を取得
        total = query.count()
        
        # ページネーション
        projects = query.offset(skip).limit(limit).all()
        
        # assigneeをリストに変換
        for project in projects:
            if project.assignee:
                try:
                    project.assignee = json.loads(project.assignee)
                except:
                    project.assignee = []
            else:
                project.assignee = []
        
        return ProjectListResponse(
            items=projects,
            total=total,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        logger.error(f"Error fetching projects: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching projects"
        )


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    """Get a single project by ID"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project with id {project_id} not found")
    
    # assigneeをリストに変換
    if project.assignee:
        try:
            project.assignee = json.loads(project.assignee)
        except:
            project.assignee = []
    else:
        project.assignee = []
    
    return project


@router.post("", response_model=ProjectResponse)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    """
    Create a new project
    
    Creates a new project. Statuses are shared across all projects.
    """
    project_dict = project.dict()
    
    # assigneeをJSON文字列に変換
    if project_dict.get("assignee") is not None:
        project_dict["assignee"] = json.dumps(project_dict["assignee"], ensure_ascii=False)
    
    try:
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
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating project: {e}", exc_info=True)
        raise


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: int, project_update: ProjectUpdate, db: Session = Depends(get_db)):
    """
    Update a project
    
    Updates an existing project by ID. System project (id=-1) cannot be updated.
    """
    if project_id == -1:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot update system project")
    
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project with id {project_id} not found")
    
    update_data = project_update.dict(exclude_unset=True)
    
    if "assignee" in update_data and update_data["assignee"] is not None:
        update_data["assignee"] = json.dumps(update_data["assignee"], ensure_ascii=False)
    
    try:
        with db_transaction(db):
            for field, value in update_data.items():
                setattr(db_project, field, value)
            
            db.commit()
            db.refresh(db_project)
            
            # レスポンス用にassigneeをリストに変換
            if db_project.assignee:
                try:
                    db_project.assignee = json.loads(db_project.assignee)
                except:
                    db_project.assignee = []
            else:
                db_project.assignee = []
            
            logger.info(f"Project {project_id} updated successfully")
            return db_project
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating project {project_id}: {e}", exc_info=True)
        raise


@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    """
    Delete a project
    
    Deletes a project by ID. System project (id=-1) cannot be deleted.
    Related tasks are also deleted due to cascade.
    """
    if project_id == -1:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot delete system project")
    
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project with id {project_id} not found")
    
    try:
        with db_transaction(db):
            db.delete(db_project)
            db.commit()
            logger.info(f"Project {project_id} deleted successfully")
            return {"message": "Project deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting project {project_id}: {e}", exc_info=True)
        raise
