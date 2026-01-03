from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from typing import List
import os
import traceback

from database import get_db, init_db
from models import Task, Status, Project, Todo
from schemas import TaskCreate, TaskUpdate, TaskResponse
from status_schemas import StatusCreate, StatusUpdate, StatusResponse
from project_schemas import ProjectCreate, ProjectUpdate, ProjectResponse
from todo_schemas import TodoCreate, TodoUpdate, TodoResponse

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

# バリデーションエラーハンドラー（RequestValidationErrorは先に処理）
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """バリデーションエラーをキャッチして、CORSヘッダーを含む適切なHTTPレスポンスを返す"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )

# グローバル例外ハンドラー（CORSヘッダーを含む適切なエラーレスポンスを返す）
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """すべての例外をキャッチして、適切なHTTPレスポンスとCORSヘッダーを返す"""
    error_trace = traceback.format_exc()
    print(f"Unhandled exception: {exc}")
    print(f"Traceback: {error_trace}")
    
    # HTTPExceptionの場合はそのまま返す（CORSヘッダーを追加）
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "*",
            }
        )
    
    # SQLAlchemyエラーの場合
    from sqlalchemy.exc import SQLAlchemyError
    if isinstance(exc, SQLAlchemyError):
        print(f"Database error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Database error occurred"},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "*",
            }
        )
    
    # その他の例外は500エラーとして返す
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": f"Internal server error: {str(exc)}"},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
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
    
    try:
        from migrate_add_project_fields import migrate as migrate_project_fields
        migrate_project_fields()
    except Exception as e:
        print(f"プロジェクトフィールドマイグレーションエラー（無視可能）: {e}")
    
    try:
        from migrate_add_task_assignee import migrate as migrate_task_assignee
        migrate_task_assignee()
    except Exception as e:
        print(f"タスク担当者マイグレーションエラー（無視可能）: {e}")
    
    try:
        from migrate_add_personal_task_support import migrate as migrate_personal_task
        migrate_personal_task()
    except Exception as e:
        print(f"個人タスクサポートマイグレーションエラー（無視可能）: {e}")
    
    try:
        from migrate_update_statuses import migrate as migrate_update_statuses
        migrate_update_statuses()
    except Exception as e:
        print(f"ステータス更新マイグレーションエラー（無視可能）: {e}")
    
    try:
        from migrate_add_todos import migrate as migrate_todos
        migrate_todos()
    except Exception as e:
        print(f"todosテーブル作成マイグレーションエラー（無視可能）: {e}")
    
    try:
        from migrate_add_todo_dates import migrate as migrate_todo_dates
        migrate_todo_dates()
    except Exception as e:
        print(f"TODO日付カラム追加マイグレーションエラー（無視可能）: {e}")
    
    # デフォルトステータスの初期化（各プロジェクトごと）
    from database import SessionLocal
    db = SessionLocal()
    try:
        projects = db.query(Project).all()
        default_statuses = [
            {"name": "considering", "display_name": "検討中", "order": 0, "color": "#9e9e9e"},
            {"name": "not_started", "display_name": "未実行", "order": 1, "color": "#667eea"},
            {"name": "in_progress", "display_name": "実行中", "order": 2, "color": "#ffa726"},
            {"name": "review_pending", "display_name": "レビュー待ち", "order": 3, "color": "#9c27b0"},
            {"name": "staging_deployed", "display_name": "検証環境反映済み", "order": 4, "color": "#ffeb3b"},
            {"name": "production_deployed", "display_name": "本番環境反映済み", "order": 5, "color": "#51cf66"},
            {"name": "cancelled", "display_name": "中止", "order": 6, "color": "#dc3545"}
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
def get_tasks(project_id: int = None, project_ids: str = None, assignee: str = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    print(f"get_tasks called with project_id={project_id}, project_ids={project_ids}, assignee={assignee}")
    # status_idで並べ替え、同じstatus_id内ではorderで並べ替え
    from sqlalchemy import nullslast
    query = db.query(Task)
    if project_id is not None:
        query = query.filter(Task.project_id == project_id)
        # assigneeが指定されている場合は、そのプロジェクトのタスクでassigneeが一致するもののみ
        if assignee:
            if project_id == -1:
                print(f"Filtering for project_id=-1 and assignee={assignee}")
            else:
                print(f"Filtering for project_id={project_id} and assignee={assignee}")
            query = query.filter(Task.assignee == assignee)
    elif project_ids:
        # カンマ区切りのプロジェクトIDリスト
        project_id_list = [int(pid.strip()) for pid in project_ids.split(',') if pid.strip()]
        if project_id_list:
            # -1が含まれている場合は個人タスクを含む
            if -1 in project_id_list:
                # -1以外のプロジェクトIDと、-1かつassigneeが一致するタスク
                other_project_ids = [pid for pid in project_id_list if pid != -1]
                if other_project_ids:
                    if assignee:
                        # -1以外のプロジェクトIDでassigneeが一致するタスクと、-1かつassigneeが一致するタスク
                        print(f"Filtering for project_ids={other_project_ids} with assignee={assignee} OR project_id=-1 with assignee={assignee}")
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
                    # -1のみの場合
                    if assignee:
                        print(f"Filtering for project_id=-1 with assignee={assignee}")
                        query = query.filter((Task.project_id == -1) & (Task.assignee == assignee))
                    else:
                        query = query.filter(Task.project_id == -1)
            else:
                # -1以外のプロジェクトIDのみの場合
                if assignee:
                    # assigneeが指定されている場合は、そのプロジェクトのタスクでassigneeが一致するもののみ
                    query = query.filter(
                        (Task.project_id.in_(project_id_list)) & (Task.assignee == assignee)
                    )
                else:
                    query = query.filter(Task.project_id.in_(project_id_list))
    elif assignee:
        # assigneeのみが指定された場合、project_id=-1のタスクを取得
        query = query.filter((Task.project_id == -1) & (Task.assignee == assignee))
    tasks = query.order_by(
        nullslast(Task.status_id),
        Task.order
    ).offset(skip).limit(limit).all()
    print(f"Returning {len(tasks)} tasks")
    # デバッグ用：最初の数件のタスク情報を出力
    if len(tasks) > 0:
        for i, task in enumerate(tasks[:3]):
            print(f"Task {i}: id={task.id}, project_id={task.project_id}, assignee={task.assignee}, title={task.title}")
    else:
        # タスクが0件の場合、条件に合うタスクが存在するか確認
        test_query = db.query(Task).filter(Task.project_id == -1)
        all_personal_tasks = test_query.all()
        print(f"Total personal tasks (project_id=-1): {len(all_personal_tasks)}")
        if assignee:
            test_query_with_assignee = db.query(Task).filter(Task.project_id == -1, Task.assignee == assignee)
            matching_tasks = test_query_with_assignee.all()
            print(f"Personal tasks with assignee={assignee}: {len(matching_tasks)}")
            if len(matching_tasks) > 0:
                for task in matching_tasks[:3]:
                    print(f"  - Task id={task.id}, assignee={task.assignee}, title={task.title}")
    return tasks

@app.get("/api/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.post("/api/tasks", response_model=TaskResponse)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    # project_id=-1の場合は個人タスク（外部キー制約を回避するため、特別な処理は不要）
    # ただし、project_id=-1の場合はassigneeが必須
    if task.project_id == -1 and not task.assignee:
        raise HTTPException(status_code=400, detail="Assignee is required for personal tasks (project_id=-1)")
    
    task_dict = task.dict()
    
    # status_idが指定されていない場合、status名から取得
    if task_dict.get("status_id") is None and task_dict.get("status"):
        status_name = task_dict["status"]
        project_id = task_dict["project_id"]
        
        if project_id == -1:
            # 個人タスクの場合はstatus_idはNoneのまま
            task_dict["status_id"] = None
        else:
            # プロジェクトのステータスからIDを取得
            status = db.query(Status).filter(
                Status.name == status_name,
                Status.project_id == project_id
            ).first()
            if status:
                task_dict["status_id"] = status.id
    
    db_task = Task(**task_dict)
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
    
    # プロジェクトIDを取得（更新データまたは既存のタスクから）
    project_id = update_data.get("project_id", db_task.project_id)
    
    # ステータスが変更された場合、status_idも更新
    if "status" in update_data:
        status_name = update_data["status"]
        # project_id=-1の場合は個人タスクで、status_idはNULLにする
        if project_id == -1:
            update_data["status_id"] = None
        else:
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
        status_name = update_data.get("status", db_task.status)
        
        # project_id=-1の場合は、status名とassigneeでフィルタリング
        if project_id == -1:
            # 同じステータス内のタスクを取得（同じプロジェクトIDとassignee）
            assignee = update_data.get("assignee", db_task.assignee)
            same_status_tasks = db.query(Task).filter(
                Task.status == status_name,
                Task.project_id == -1,
                Task.assignee == assignee,
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
        else:
            # status_idがNoneの場合は、status名から取得
            if status_id is None and "status" in update_data:
                status = db.query(Status).filter(
                    Status.name == status_name,
                    Status.project_id == project_id
                ).first()
                if status:
                    status_id = status.id
                    update_data["status_id"] = status_id
            
            if status_id is not None:
                # 同じステータス内のタスクを取得（同じプロジェクト内）
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
    try:
        print(f"get_statuses called with project_id={project_id}")
        # project_id=-1の場合は個人タスク用のデフォルトステータスを返す
        if project_id == -1:
            # 個人タスク用のデフォルトステータス（仮想的なIDを使用）
            from datetime import datetime
            default_statuses = [
                {"id": -1, "name": "considering", "display_name": "検討中", "order": 0, "color": "#9e9e9e", "project_id": -1, "created_at": datetime.now()},
                {"id": -2, "name": "not_started", "display_name": "未実行", "order": 1, "color": "#667eea", "project_id": -1, "created_at": datetime.now()},
                {"id": -3, "name": "in_progress", "display_name": "実行中", "order": 2, "color": "#ffa726", "project_id": -1, "created_at": datetime.now()},
                {"id": -4, "name": "review_pending", "display_name": "レビュー待ち", "order": 3, "color": "#9c27b0", "project_id": -1, "created_at": datetime.now()},
                {"id": -5, "name": "staging_deployed", "display_name": "検証環境反映済み", "order": 4, "color": "#ffeb3b", "project_id": -1, "created_at": datetime.now()},
                {"id": -6, "name": "production_deployed", "display_name": "本番環境反映済み", "order": 5, "color": "#51cf66", "project_id": -1, "created_at": datetime.now()},
                {"id": -7, "name": "cancelled", "display_name": "中止", "order": 6, "color": "#dc3545", "project_id": -1, "created_at": datetime.now()}
            ]
            result = [StatusResponse(**status) for status in default_statuses]
            print(f"Returning {len(result)} default statuses for project_id=-1")
            return result
        
        query = db.query(Status)
        if project_id is not None:
            query = query.filter(Status.project_id == project_id)
        statuses = query.order_by(Status.order).all()
        print(f"Returning {len(statuses)} statuses from database for project_id={project_id}")
        return statuses
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error in get_statuses: {e}")
        print(f"Traceback: {error_trace}")
        raise HTTPException(status_code=500, detail=f"Error fetching statuses: {str(e)}")

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
def get_projects(assignee: str = None, db: Session = Depends(get_db)):
    import json
    query = db.query(Project)
    
    # 担当者でフィルタリング
    if assignee:
        # assigneeカラムに担当者が含まれるプロジェクトを検索
        # JSON配列として保存されているため、LIKE検索を使用
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

@app.get("/api/projects/personal/{username}", response_model=ProjectResponse)
def get_or_create_personal_project(username: str, db: Session = Depends(get_db)):
    """
    個人的タスク用のプロジェクトを取得または作成（非推奨）
    
    注意: このエンドポイントは非推奨です。
    個人タスクはプロジェクトID=-1で扱うように変更されました。
    このエンドポイントは後方互換性のため残されていますが、使用しないでください。
    """
    raise HTTPException(
        status_code=410, 
        detail="This endpoint is deprecated. Personal tasks should use project_id=-1 instead."
    )

@app.get("/api/projects/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    import json
    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    # assigneeをリストに変換
    if project.assignee:
        try:
            project.assignee = json.loads(project.assignee)
        except:
            project.assignee = []
    else:
        project.assignee = []
    return project

@app.post("/api/projects", response_model=ProjectResponse)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    import json
    project_dict = project.dict()
    # assigneeをJSON文字列に変換
    if project_dict.get("assignee"):
        project_dict["assignee"] = json.dumps(project_dict["assignee"], ensure_ascii=False)
    else:
        project_dict["assignee"] = None
    
    db_project = Project(**project_dict)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    
    # デフォルトステータスを作成
    default_statuses = [
        {"name": "considering", "display_name": "検討中", "order": 0, "color": "#9e9e9e", "project_id": db_project.id},
        {"name": "not_started", "display_name": "未実行", "order": 1, "color": "#667eea", "project_id": db_project.id},
        {"name": "in_progress", "display_name": "実行中", "order": 2, "color": "#ffa726", "project_id": db_project.id},
        {"name": "review_pending", "display_name": "レビュー待ち", "order": 3, "color": "#9c27b0", "project_id": db_project.id},
        {"name": "staging_deployed", "display_name": "検証環境反映済み", "order": 4, "color": "#ffeb3b", "project_id": db_project.id},
        {"name": "production_deployed", "display_name": "本番環境反映済み", "order": 5, "color": "#51cf66", "project_id": db_project.id},
        {"name": "cancelled", "display_name": "中止", "order": 6, "color": "#dc3545", "project_id": db_project.id}
    ]
    
    for status_data in default_statuses:
        db_status = Status(**status_data)
        db.add(db_status)
    
    db.commit()
    db.refresh(db_project)
    
    # レスポンス用にassigneeをリストに変換
    if db_project.assignee:
        db_project.assignee = json.loads(db_project.assignee)
    else:
        db_project.assignee = []
    
    return db_project

@app.put("/api/projects/{project_id}", response_model=ProjectResponse)
def update_project(project_id: int, project_update: ProjectUpdate, db: Session = Depends(get_db)):
    import json
    # システム用プロジェクト（id=-1）は更新不可
    if project_id == -1:
        raise HTTPException(status_code=403, detail="Cannot update system project (id=-1)")
    
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    update_data = project_update.dict(exclude_unset=True)
    # assigneeをJSON文字列に変換
    if "assignee" in update_data and update_data["assignee"] is not None:
        update_data["assignee"] = json.dumps(update_data["assignee"], ensure_ascii=False)
    
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

@app.delete("/api/projects/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    # システム用プロジェクト（id=-1）は削除不可
    if project_id == -1:
        raise HTTPException(status_code=403, detail="Cannot delete system project (id=-1)")
    
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # プロジェクトを削除すると、関連するタスクとステータスも自動的に削除される（CASCADE）
    db.delete(db_project)
    db.commit()
    return {"message": "Project deleted successfully"}

# TODO管理API
@app.get("/api/tasks/{task_id}/todos", response_model=List[TodoResponse])
def get_todos(task_id: int, db: Session = Depends(get_db)):
    # タスクの存在確認
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    todos = db.query(Todo).filter(Todo.task_id == task_id).order_by(Todo.order).all()
    return todos

# すべてのTODOを取得（ページネーション対応、タスク情報とプロジェクト情報を含む）
@app.get("/api/todos")
def get_all_todos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    from sqlalchemy.orm import joinedload
    
    # TODOを取得（タスクとプロジェクト情報をJOIN、LEFT JOINで個人タスクも含める）
    query = db.query(Todo).join(Task, Todo.task_id == Task.id).outerjoin(
        Project, Task.project_id == Project.id
    )
    
    # 総件数を取得
    total = query.count()
    
    # ページネーション適用
    todos = query.order_by(Todo.order).offset(skip).limit(limit).all()
    
    # レスポンス用のデータを構築
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
            "project_name": "個人タスク" if task and task.project_id == -1 else (project.name if project else None),
        })
    
    return {
        "items": result,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@app.post("/api/tasks/{task_id}/todos", response_model=TodoResponse)
def create_todo(task_id: int, todo: TodoCreate, db: Session = Depends(get_db)):
    # タスクの存在確認
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # task_idを設定
    todo_dict = todo.dict()
    todo_dict["task_id"] = task_id
    
    # date型をdatetime型に変換（SQLAlchemyのDateTimeカラム用）
    from datetime import datetime, date
    if todo_dict.get("scheduled_date") and isinstance(todo_dict["scheduled_date"], date):
        todo_dict["scheduled_date"] = datetime.combine(todo_dict["scheduled_date"], datetime.min.time())
    if todo_dict.get("completed_date") and isinstance(todo_dict["completed_date"], date):
        todo_dict["completed_date"] = datetime.combine(todo_dict["completed_date"], datetime.min.time())
    
    db_todo = Todo(**todo_dict)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

@app.put("/api/todos/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, todo_update: TodoUpdate, db: Session = Depends(get_db)):
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    update_data = todo_update.dict(exclude_unset=True)
    
    # date型をdatetime型に変換（SQLAlchemyのDateTimeカラム用）
    from datetime import datetime, date
    if "scheduled_date" in update_data and update_data["scheduled_date"] is not None:
        if isinstance(update_data["scheduled_date"], date):
            update_data["scheduled_date"] = datetime.combine(update_data["scheduled_date"], datetime.min.time())
    if "completed_date" in update_data and update_data["completed_date"] is not None:
        if isinstance(update_data["completed_date"], date):
            update_data["completed_date"] = datetime.combine(update_data["completed_date"], datetime.min.time())
    
    # 実行完了日が設定された場合は自動的にcompletedをtrueに、削除された場合はfalseに
    if "completed_date" in update_data:
        if update_data["completed_date"] is not None:
            # 実行完了日が設定された場合はcompletedをtrueに
            update_data["completed"] = True
        else:
            # 実行完了日が削除された場合はcompletedをfalseに
            update_data["completed"] = False
    
    # completedが直接指定されている場合は、completed_dateに基づいて上書きしない
    # （フロントエンドからcompleted_dateとcompletedの両方が送られてきた場合のため）
    
    for field, value in update_data.items():
        setattr(db_todo, field, value)
    
    db.commit()
    db.refresh(db_todo)
    return db_todo

@app.delete("/api/todos/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    db.delete(db_todo)
    db.commit()
    return {"message": "Todo deleted successfully"}
