"""
Application startup events
"""
from app.core.database import init_db


def run_migrations():
    """Run database migrations"""
    import sys
    import os
    # マイグレーションファイルはbackendディレクトリ直下にあるため、パスを追加
    backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    sys.path.insert(0, backend_dir)
    
    try:
        from app.migrations.migrate_add_status_id import migrate
        migrate()
    except Exception as e:
        print(f"マイグレーションエラー（無視可能）: {e}")
    
    try:
        from app.migrations.migrate_add_order import migrate as migrate_order
        migrate_order()
    except Exception as e:
        print(f"マイグレーションエラー（無視可能）: {e}")
    
    try:
        from app.migrations.migrate_add_project import migrate as migrate_project
        migrate_project()
    except Exception as e:
        print(f"プロジェクトマイグレーションエラー（無視可能）: {e}")
    
    try:
        from app.migrations.migrate_add_project_fields import migrate as migrate_project_fields
        migrate_project_fields()
    except Exception as e:
        print(f"プロジェクトフィールドマイグレーションエラー（無視可能）: {e}")
    
    try:
        from app.migrations.migrate_add_task_assignee import migrate as migrate_task_assignee
        migrate_task_assignee()
    except Exception as e:
        print(f"タスク担当者マイグレーションエラー（無視可能）: {e}")
    
    try:
        from app.migrations.migrate_add_personal_task_support import migrate as migrate_personal_task
        migrate_personal_task()
    except Exception as e:
        print(f"個人タスクサポートマイグレーションエラー（無視可能）: {e}")
    
    try:
        from app.migrations.migrate_update_statuses import migrate as migrate_update_statuses
        migrate_update_statuses()
    except Exception as e:
        print(f"ステータス更新マイグレーションエラー（無視可能）: {e}")
    
    try:
        from app.migrations.migrate_add_todos import migrate as migrate_add_todos
        migrate_add_todos()
    except Exception as e:
        print(f"todosテーブル作成マイグレーションエラー（無視可能）: {e}")
    
    try:
        from app.migrations.migrate_add_todo_dates import migrate as migrate_add_todo_dates
        migrate_add_todo_dates()
    except Exception as e:
        print(f"TODO日付カラム追加マイグレーションエラー（無視可能）: {e}")


def initialize_default_statuses():
    """Initialize default statuses for all projects"""
    from app.core.database import SessionLocal
    from app.models import Project, Status
    from app.core.constants import DEFAULT_STATUS_DEFINITIONS
    
    db = SessionLocal()
    try:
        projects = db.query(Project).all()
        
        for project in projects:
            for status_data in DEFAULT_STATUS_DEFINITIONS:
                existing = db.query(Status).filter(
                    Status.name == status_data["name"],
                    Status.project_id == project.id
                ).first()
                if not existing:
                    status = Status(**status_data, project_id=project.id)
                    db.add(status)
        
        db.commit()
    except Exception as e:
        print(f"初期化エラー（無視可能）: {e}")
    finally:
        db.close()


def startup_event():
    """Application startup event"""
    init_db()
    run_migrations()
    initialize_default_statuses()
