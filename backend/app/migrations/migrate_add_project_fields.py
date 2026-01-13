"""
プロジェクトテーブルにstart_month、end_month、assigneeフィールドを追加するマイグレーション
"""

from sqlalchemy import text

from app.core.database import engine


def migrate():
    with engine.connect() as conn:
        # start_monthカラムを追加（既に存在する場合はスキップ）
        try:
            conn.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS start_month VARCHAR"))
            conn.commit()
            print("start_monthカラムを追加しました")
        except Exception as e:
            print(f"start_monthカラム追加エラー（無視可能）: {e}")
            conn.rollback()

        # end_monthカラムを追加（既に存在する場合はスキップ）
        try:
            conn.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS end_month VARCHAR"))
            conn.commit()
            print("end_monthカラムを追加しました")
        except Exception as e:
            print(f"end_monthカラム追加エラー（無視可能）: {e}")
            conn.rollback()

        # assigneeカラムを追加（既に存在する場合はスキップ）
        try:
            conn.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS assignee TEXT"))
            conn.commit()
            print("assigneeカラムを追加しました")
        except Exception as e:
            print(f"assigneeカラム追加エラー（無視可能）: {e}")
            conn.rollback()


if __name__ == "__main__":
    migrate()
