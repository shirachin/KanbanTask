"""
既存のデータベースにorderカラムを追加するマイグレーションスクリプト
"""
from sqlalchemy import create_engine, text
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://taskapp:taskapp_password@db:5432/taskapp_db")

def migrate():
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            # orderカラムが存在するか確認
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='tasks' AND column_name='order'
            """))
            
            if result.fetchone() is None:
                print("orderカラムを追加しています...")
                conn.execute(text("""
                    ALTER TABLE tasks 
                    ADD COLUMN "order" INTEGER DEFAULT 0
                """))
                
                # 既存のタスクにorderを設定（created_at順）
                conn.execute(text("""
                    UPDATE tasks t1
                    SET "order" = (
                        SELECT COUNT(*) 
                        FROM tasks t2 
                        WHERE t2.status = t1.status 
                        AND t2.created_at <= t1.created_at
                    ) - 1
                """))
                
                trans.commit()
                print("マイグレーションが完了しました！")
            else:
                print("orderカラムは既に存在します。")
                trans.rollback()
        except Exception as e:
            trans.rollback()
            print(f"エラーが発生しました: {e}")
            raise

if __name__ == "__main__":
    migrate()
