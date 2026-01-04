"""
todosテーブルにscheduled_dateとcompleted_dateカラムを追加するマイグレーション
"""
from sqlalchemy import text
from app.core.database import engine

def migrate():
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            # scheduled_dateカラムが存在するか確認
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='todos' AND column_name='scheduled_date'
            """))
            
            if result.fetchone() is None:
                print("scheduled_dateカラムを追加しています...")
                conn.execute(text("""
                    ALTER TABLE todos 
                    ADD COLUMN scheduled_date TIMESTAMP WITH TIME ZONE
                """))
                print("scheduled_dateカラムを追加しました")
            else:
                print("scheduled_dateカラムは既に存在します")
            
            # completed_dateカラムが存在するか確認
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='todos' AND column_name='completed_date'
            """))
            
            if result.fetchone() is None:
                print("completed_dateカラムを追加しています...")
                conn.execute(text("""
                    ALTER TABLE todos 
                    ADD COLUMN completed_date TIMESTAMP WITH TIME ZONE
                """))
                print("completed_dateカラムを追加しました")
            else:
                print("completed_dateカラムは既に存在します")
            
            trans.commit()
        except Exception as e:
            trans.rollback()
            print(f"TODO日付カラム追加マイグレーションエラー: {e}")
            raise

if __name__ == "__main__":
    migrate()
