"""
todosテーブルを作成するマイグレーション
"""
from sqlalchemy import text
from database import engine

def migrate():
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            # todosテーブルが存在するか確認
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name='todos'
            """))
            
            if result.fetchone() is None:
                print("todosテーブルを作成しています...")
                conn.execute(text("""
                    CREATE TABLE todos (
                        id SERIAL PRIMARY KEY,
                        task_id INTEGER NOT NULL,
                        title VARCHAR NOT NULL,
                        completed BOOLEAN DEFAULT FALSE,
                        "order" INTEGER DEFAULT 0,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP WITH TIME ZONE,
                        CONSTRAINT fk_todos_task 
                            FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
                    )
                """))
                
                # インデックスを作成
                conn.execute(text("CREATE INDEX IF NOT EXISTS idx_todos_task_id ON todos(task_id)"))
                
                print("todosテーブルを作成しました")
            else:
                print("todosテーブルは既に存在します")
            
            trans.commit()
        except Exception as e:
            trans.rollback()
            print(f"todosテーブル作成マイグレーションエラー: {e}")
            raise

if __name__ == "__main__":
    migrate()
