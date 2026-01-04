"""
タスクテーブルにassigneeフィールドを追加するマイグレーション
"""
from sqlalchemy import text
from app.core.database import engine

def migrate():
    with engine.connect() as conn:
        # assigneeカラムを追加（既に存在する場合はスキップ）
        try:
            conn.execute(text("ALTER TABLE tasks ADD COLUMN IF NOT EXISTS assignee VARCHAR"))
            conn.commit()
            print("tasksテーブルにassigneeカラムを追加しました")
        except Exception as e:
            print(f"assigneeカラム追加エラー（無視可能）: {e}")
            conn.rollback()

if __name__ == "__main__":
    migrate()
