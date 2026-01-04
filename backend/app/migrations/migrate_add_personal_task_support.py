"""
個人タスク（project_id=-1）をサポートするためのマイグレーション
ダミープロジェクト（id=-1）を作成して外部キー制約を満たす
"""
from sqlalchemy import text
from app.core.database import engine

def migrate():
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            # id=-1のダミープロジェクトが存在するか確認
            result = conn.execute(text("SELECT id FROM projects WHERE id = -1"))
            if result.fetchone() is None:
                # id=-1のダミープロジェクトを作成（シーケンスを無視して直接挿入）
                conn.execute(text("""
                    INSERT INTO projects (id, name, description) 
                    VALUES (-1, '個人タスク（システム用）', '個人タスク用のダミープロジェクト。このプロジェクトは削除しないでください。')
                """))
                print("個人タスク用ダミープロジェクト（id=-1）を作成しました")
            else:
                print("個人タスク用ダミープロジェクト（id=-1）は既に存在します")
            
            trans.commit()
        except Exception as e:
            trans.rollback()
            print(f"個人タスクサポートマイグレーションエラー（無視可能）: {e}")

if __name__ == "__main__":
    migrate()
