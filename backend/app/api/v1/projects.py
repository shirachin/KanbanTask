"""
Project API routes
"""
import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.core.database import get_db
from app.models import Project, Status
from app.schemas import ProjectCreate, ProjectUpdate, ProjectResponse
from app.core.constants import DEFAULT_STATUS_DEFINITIONS

router = APIRouter()


@router.get("", response_model=List[ProjectResponse])
def get_projects(assignee: Optional[str] = None, db: Session = Depends(get_db)):
    """Get all projects"""
    query = db.query(Project)
    
    if assignee:
        query = query.filter(Project.assignee.like(f'%"{assignee}"%'))
    
    projects = query.order_by(Project.created_at.desc()).all()
    
    # assigneeをリストに変換
    for project in projects:
        if project.assignee:
            try:
                project.assignee = json.loads(project.assignee)
            except:
                project.assignee = []
        else:
            project.assignee = []
    
    return projects


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
    """Create a new project"""
    project_dict = project.dict()
    
    # assigneeをJSON文字列に変換
    if project_dict.get("assignee") is not None:
        project_dict["assignee"] = json.dumps(project_dict["assignee"], ensure_ascii=False)
    
    try:
        db_project = Project(**project_dict)
        db.add(db_project)
        db.flush()
        
        # デフォルトステータスを作成
        for status_data in DEFAULT_STATUS_DEFINITIONS:
            db_status = Status(**status_data, project_id=db_project.id)
            db.add(db_status)
        
        db.commit()
        db.refresh(db_project)
        
        # レスポンス用にassigneeをリストに変換
        if db_project.assignee:
            db_project.assignee = json.loads(db_project.assignee)
        else:
            db_project.assignee = []
        
        return db_project
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create project due to database constraints"
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )
    except Exception as e:
        db.rollback()
        raise


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: int, project_update: ProjectUpdate, db: Session = Depends(get_db)):
    """Update a project"""
    if project_id == -1:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot update system project")
    
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project with id {project_id} not found")
    
    update_data = project_update.dict(exclude_unset=True)
    
    if "assignee" in update_data and update_data["assignee"] is not None:
        update_data["assignee"] = json.dumps(update_data["assignee"], ensure_ascii=False)
    
    try:
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
        
        return db_project
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update project due to database constraints"
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )
    except Exception as e:
        db.rollback()
        raise


@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    """Delete a project"""
    if project_id == -1:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot delete system project")
    
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project with id {project_id} not found")
    
    try:
        db.delete(db_project)
        db.commit()
        return {"message": "Project deleted successfully"}
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete project due to related data constraints"
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )
    except Exception as e:
        db.rollback()
        raise
