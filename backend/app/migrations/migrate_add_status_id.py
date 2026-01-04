"""
既存のデータベースにstatus_idカラムを追加するマイグレーションスクリプト
"""
from sqlalchemy import create_engine, text
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://taskapp:taskapp_password@db:5432/taskapp_db")

def migrate():
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            # status_idカラムが存在するか確認
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='tasks' AND column_name='status_id'
            """))
            
            if result.fetchone() is None:
                print("status_idカラムを追加しています...")
                conn.execute(text("""
                    ALTER TABLE tasks 
                    ADD COLUMN status_id INTEGER
                """))
                
                # statusesテーブルが存在しない場合は作成
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS statuses (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR NOT NULL UNIQUE,
                        display_name VARCHAR NOT NULL,
                        "order" INTEGER DEFAULT 0,
                        color VARCHAR DEFAULT '#667eea',
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # デフォルトステータスを追加
                default_statuses = [
                    ("todo", "To Do", 0, "#667eea"),
                    ("doing", "Doing", 1, "#ffa726"),
                    ("done", "Done", 2, "#51cf66")
                ]
                
                for name, display_name, order, color in default_statuses:
                    conn.execute(text("""
                        INSERT INTO statuses (name, display_name, "order", color)
                        VALUES (:name, :display_name, :order, :color)
                        ON CONFLICT (name) DO NOTHING
                    """), {"name": name, "display_name": display_name, "order": order, "color": color})
                
                # 既存のタスクのstatus_idを更新
                conn.execute(text("""
                    UPDATE tasks t
                    SET status_id = s.id
                    FROM statuses s
                    WHERE t.status = s.name
                """))
                
                trans.commit()
                print("マイグレーションが完了しました！")
            else:
                print("status_idカラムは既に存在します。")
                trans.rollback()
        except Exception as e:
            trans.rollback()
            print(f"エラーが発生しました: {e}")
            raise

if __name__ == "__main__":
    migrate()
