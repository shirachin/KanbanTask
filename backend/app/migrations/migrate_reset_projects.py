"""
既存のプロジェクトをすべて削除し、新しいテストプロジェクトを登録するマイグレーション
"""
from sqlalchemy import text
from app.core.database import engine

# 新しいテストプロジェクトのリスト
NEW_PROJECTS = [
    "【25/1Q】プロジェクトA",
    "【25/1Q】プロジェクトB",
    "【25/1Q】プロジェクトC",
    "【25/1Q】プロジェクトD",
    "【25/2Q】プロジェクトA",
    "【25/2Q】プロジェクトB",
    "【25/2Q】プロジェクトC",
    "【25/2Q】プロジェクトD",
    "【25/3Q】プロジェクトA",
    "【25/3Q】プロジェクトB",
    "【25/3Q】プロジェクトC",
    "【25/3Q】プロジェクトD",
    "【25/4Q】プロジェクトA",
    "【25/4Q】プロジェクトB",
    "【25/4Q】プロジェクトC",
    "【25/4Q】プロジェクトD",
    "【26/1Q】プロジェクトA",
    "【26/1Q】プロジェクトB",
    "【26/1Q】プロジェクトC",
    "【26/1Q】プロジェクトD",
    "【26/2Q】プロジェクトA",
    "【26/2Q】プロジェクトB",
    "【26/2Q】プロジェクトC",
    "【26/2Q】プロジェクトD",
    "【26/3Q】プロジェクトA",
    "【26/3Q】プロジェクトB",
    "【26/3Q】プロジェクトC",
    "【26/3Q】プロジェクトD",
    "【26/4Q】プロジェクトA",
    "【26/4Q】プロジェクトB",
    "【26/4Q】プロジェクトC",
    "【26/4Q】プロジェクトD",
    "【27/1Q】プロジェクトA",
    "【27/1Q】プロジェクトB",
    "【27/1Q】プロジェクトC",
    "【27/1Q】プロジェクトD",
    "【27/2Q】プロジェクトA",
    "【27/2Q】プロジェクトB",
    "【27/2Q】プロジェクトC",
    "【27/2Q】プロジェクトD",
    "【27/3Q】プロジェクトA",
    "【27/3Q】プロジェクトB",
    "【27/3Q】プロジェクトC",
    "【27/3Q】プロジェクトD",
    "【27/4Q】プロジェクトA",
    "【27/4Q】プロジェクトB",
    "【27/4Q】プロジェクトC",
    "【27/4Q】プロジェクトD",
    "【28/1Q】プロジェクトA",
    "【28/1Q】プロジェクトB",
    "【28/1Q】プロジェクトC",
    "【28/1Q】プロジェクトD",
    "【28/2Q】プロジェクトA",
    "【28/2Q】プロジェクトB",
    "【28/2Q】プロジェクトC",
    "【28/2Q】プロジェクトD",
    "【28/3Q】プロジェクトA",
    "【28/3Q】プロジェクトB",
    "【28/3Q】プロジェクトC",
    "【28/3Q】プロジェクトD",
    "【28/4Q】プロジェクトA",
    "【28/4Q】プロジェクトB",
    "【28/4Q】プロジェクトC",
    "【28/4Q】プロジェクトD",
]

def migrate():
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            # 1. 個人タスク（id=-1）以外のすべてのプロジェクトを削除
            # まず、関連するタスクとステータスを削除（CASCADEで自動削除されるが、明示的に削除）
            print("既存のプロジェクトを削除中...")
            conn.execute(text("DELETE FROM projects WHERE id != -1"))
            
            # 2. 新しいプロジェクトを登録
            print(f"{len(NEW_PROJECTS)}個の新しいプロジェクトを登録中...")
            for project_name in NEW_PROJECTS:
                conn.execute(text("""
                    INSERT INTO projects (name, description, start_month, end_month, assignee, created_at)
                    VALUES (:name, NULL, NULL, NULL, NULL, NOW())
                """), {"name": project_name})
            
            trans.commit()
            print(f"マイグレーションが完了しました。{len(NEW_PROJECTS)}個のプロジェクトを登録しました。")
        except Exception as e:
            trans.rollback()
            print(f"マイグレーションエラー: {e}")
            raise

if __name__ == "__main__":
    migrate()
