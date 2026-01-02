from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
import os

from database import get_db, init_db
from models import Task, Status, Project
from schemas import TaskCreate, TaskUpdate, TaskResponse
from status_schemas import StatusCreate, StatusUpdate, StatusResponse
from project_schemas import ProjectCreate, ProjectUpdate, ProjectResponse

app = FastAPI(title="Task Management API")

# CORS設定（最初に追加する必要がある）
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
# 空文字列を削除
cors_origins = [origin.strip() for origin in cors_origins if origin.strip()]
# 開発環境ではすべてのオリジンを許可（本番環境では適切に制限してください）
is_development = os.getenv("ENVIRONMENT", "development") == "development"
if is_development:
    # すべてのオリジンを許可する場合、allow_credentialsはFalseにする必要がある
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

# データベース初期化
@app.on_event("startup")
def startup_event():
    init_db()
    # マイグレーションを実行
    try:
        from migrate_add_status_id import migrate
        migrate()
    except Exception as e:
        print(f"マイグレーションエラー（無視可能）: {e}")
    
    try:
        from migrate_add_order import migrate as migrate_order
        migrate_order()
    except Exception as e:
        print(f"マイグレーションエラー（無視可能）: {e}")
    
    try:
        from migrate_add_project import migrate as migrate_project
        migrate_project()
    except Exception as e:
        print(f"プロジェクトマイグレーションエラー（無視可能）: {e}")
    
    # デフォルトステータスの初期化（各プロジェクトごと）
    from database import SessionLocal
    db = SessionLocal()
    try:
        projects = db.query(Project).all()
        default_statuses = [
            {"name": "todo", "display_name": "To Do", "order": 0, "color": "#667eea"},
            {"name": "doing", "display_name": "Doing", "order": 1, "color": "#ffa726"},
            {"name": "done", "display_name": "Done", "order": 2, "color": "#51cf66"}
        ]
        
        for project in projects:
            for status_data in default_statuses:
                existing = db.query(Status).filter(
                    Status.name == status_data["name"],
                    Status.project_id == project.id
                ).first()
                if not existing:
                    status_data_with_project = {**status_data, "project_id": project.id}
                    db_status = Status(**status_data_with_project)
                    db.add(db_status)
        
        db.commit()
    except Exception as e:
        print(f"初期化エラー（無視可能）: {e}")
        db.rollback()
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Task Management API"}

@app.get("/api/tasks", response_model=List[TaskResponse])
def get_tasks(project_id: int = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # status_idで並べ替え、同じstatus_id内ではorderで並べ替え
    from sqlalchemy import nullslast
    query = db.query(Task)
    if project_id is not None:
        query = query.filter(Task.project_id == project_id)
    tasks = query.order_by(
        nullslast(Task.status_id),
        Task.order
    ).offset(skip).limit(limit).all()
    return tasks

@app.get("/api/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.post("/api/tasks", response_model=TaskResponse)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    db_task = Task(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@app.put("/api/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    update_data = task_update.dict(exclude_unset=True)
    
    # ステータスが変更された場合、status_idも更新
    if "status" in update_data:
        status_name = update_data["status"]
        project_id = update_data.get("project_id", db_task.project_id)
        status = db.query(Status).filter(
            Status.name == status_name,
            Status.project_id == project_id
        ).first()
        if status:
            update_data["status_id"] = status.id
    
    # 順序が変更された場合、同じステータス内の他のタスクの順序を調整
    if "order" in update_data:
        new_order = update_data["order"]
        old_order = db_task.order or 0
        status_id = update_data.get("status_id", db_task.status_id)
        
        # status_idがNoneの場合は、status名から取得
        if status_id is None and "status" in update_data:
            status_name = update_data["status"]
            project_id = update_data.get("project_id", db_task.project_id)
            status = db.query(Status).filter(
                Status.name == status_name,
                Status.project_id == project_id
            ).first()
            if status:
                status_id = status.id
                update_data["status_id"] = status_id
        
        if status_id is not None:
            # 同じステータス内のタスクを取得（同じプロジェクト内）
            project_id = update_data.get("project_id", db_task.project_id)
            same_status_tasks = db.query(Task).filter(
                Task.status_id == status_id,
                Task.project_id == project_id,
                Task.id != task_id
            ).all()
            
            if new_order < old_order:
                # 上に移動: 新しい位置から古い位置までのタスクを1つ下に
                for task in same_status_tasks:
                    task_order = task.order or 0
                    if task_order >= new_order and task_order < old_order:
                        task.order = task_order + 1
            elif new_order > old_order:
                # 下に移動: 古い位置から新しい位置までのタスクを1つ上に
                for task in same_status_tasks:
                    task_order = task.order or 0
                    if task_order > old_order and task_order <= new_order:
                        task.order = task_order - 1
    
    for field, value in update_data.items():
        setattr(db_task, field, value)
    
    db.commit()
    db.refresh(db_task)
    return db_task

@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(db_task)
    db.commit()
    return {"message": "Task deleted successfully"}

# ステータス管理API
@app.get("/api/statuses", response_model=List[StatusResponse])
def get_statuses(project_id: int = None, db: Session = Depends(get_db)):
    query = db.query(Status)
    if project_id is not None:
        query = query.filter(Status.project_id == project_id)
    statuses = query.order_by(Status.order).all()
    return statuses

@app.post("/api/statuses", response_model=StatusResponse)
def create_status(status: StatusCreate, db: Session = Depends(get_db)):
    # 同じプロジェクト内での名前の重複チェック
    existing = db.query(Status).filter(
        Status.name == status.name,
        Status.project_id == status.project_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Status with this name already exists in this project")
    
    db_status = Status(**status.dict())
    db.add(db_status)
    db.commit()
    db.refresh(db_status)
    return db_status

@app.put("/api/statuses/{status_id}", response_model=StatusResponse)
def update_status(status_id: int, status_update: StatusUpdate, db: Session = Depends(get_db)):
    db_status = db.query(Status).filter(Status.id == status_id).first()
    if db_status is None:
        raise HTTPException(status_code=404, detail="Status not found")
    
    update_data = status_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_status, field, value)
    
    db.commit()
    db.refresh(db_status)
    return db_status

@app.delete("/api/statuses/{status_id}")
def delete_status(status_id: int, db: Session = Depends(get_db)):
    db_status = db.query(Status).filter(Status.id == status_id).first()
    if db_status is None:
        raise HTTPException(status_code=404, detail="Status not found")
    
    # このステータスを使用しているタスクがあるかチェック（同じプロジェクト内）
    task_count = db.query(Task).filter(
        Task.status == db_status.name,
        Task.project_id == db_status.project_id
    ).count()
    if task_count > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete status: {task_count} task(s) are using this status"
        )
    
    db.delete(db_status)
    db.commit()
    return {"message": "Status deleted successfully"}

# プロジェクト管理API
@app.get("/api/projects", response_model=List[ProjectResponse])
def get_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).order_by(Project.created_at.desc()).all()
    return projects

@app.get("/api/projects/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@app.post("/api/projects", response_model=ProjectResponse)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    db_project = Project(**project.dict())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    
    # デフォルトステータスを作成
    default_statuses = [
        {"name": "todo", "display_name": "To Do", "order": 0, "color": "#667eea", "project_id": db_project.id},
        {"name": "doing", "display_name": "Doing", "order": 1, "color": "#ffa726", "project_id": db_project.id},
        {"name": "done", "display_name": "Done", "order": 2, "color": "#51cf66", "project_id": db_project.id}
    ]
    
    for status_data in default_statuses:
        db_status = Status(**status_data)
        db.add(db_status)
    
    db.commit()
    db.refresh(db_project)
    return db_project

@app.put("/api/projects/{project_id}", response_model=ProjectResponse)
def update_project(project_id: int, project_update: ProjectUpdate, db: Session = Depends(get_db)):
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    update_data = project_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_project, field, value)
    
    db.commit()
    db.refresh(db_project)
    return db_project

@app.delete("/api/projects/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # プロジェクトを削除すると、関連するタスクとステータスも自動的に削除される（CASCADE）
    db.delete(db_project)
    db.commit()
    return {"message": "Project deleted successfully"}
