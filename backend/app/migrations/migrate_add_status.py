"""
既存のデータベースにstatusカラムを追加するマイグレーションスクリプト
"""

import os

from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://taskapp:taskapp_password@db:5432/taskapp_db")


def migrate():
    engine = create_engine(DATABASE_URL)

    with engine.connect() as conn:
        # トランザクションを開始
        trans = conn.begin()
        try:
            # statusカラムが存在するか確認
            result = conn.execute(
                text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name='tasks' AND column_name='status'
            """)
            )

            if result.fetchone() is None:
                # statusカラムを追加
                print("statusカラムを追加しています...")
                conn.execute(
                    text("""
                    ALTER TABLE tasks
                    ADD COLUMN status VARCHAR(20) DEFAULT 'todo' NOT NULL
                """)
                )

                # 既存のcompletedカラムに基づいてstatusを更新
                conn.execute(
                    text("""
                    UPDATE tasks
                    SET status = CASE
                        WHEN completed = true THEN 'done'
                        ELSE 'todo'
                    END
                """)
                )

                # Enum型に変更（PostgreSQLの場合）
                conn.execute(
                    text("""
                    ALTER TABLE tasks
                    ALTER COLUMN status TYPE VARCHAR(20)
                """)
                )

                trans.commit()
                print("マイグレーションが完了しました！")
            else:
                print("statusカラムは既に存在します。")
                trans.rollback()
        except Exception as e:
            trans.rollback()
            print(f"エラーが発生しました: {e}")
            raise


if __name__ == "__main__":
    migrate()
