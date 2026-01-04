"""
すべてのプロジェクトのステータスを新しい7つのフェーズに更新するマイグレーション
既存のステータスを削除し、新しいステータスを作成します
"""
from sqlalchemy import text
from app.core.database import engine

def migrate():
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            # 新しいステータス定義
            new_statuses = [
                {"name": "considering", "display_name": "検討中", "order": 0, "color": "#9e9e9e"},
                {"name": "not_started", "display_name": "未実行", "order": 1, "color": "#667eea"},
                {"name": "in_progress", "display_name": "実行中", "order": 2, "color": "#ffa726"},
                {"name": "review_pending", "display_name": "レビュー待ち", "order": 3, "color": "#9c27b0"},
                {"name": "staging_deployed", "display_name": "検証環境反映済み", "order": 4, "color": "#ffeb3b"},
                {"name": "production_deployed", "display_name": "本番環境反映済み", "order": 5, "color": "#51cf66"},
                {"name": "cancelled", "display_name": "中止", "order": 6, "color": "#dc3545"}
            ]
            
            # すべてのプロジェクトを取得
            projects_result = conn.execute(text("SELECT id FROM projects WHERE id != -1"))
            projects = projects_result.fetchall()
            
            for (project_id,) in projects:
                # 既存のステータスを削除（タスクとの関連は保持されるため、status_idはNULLになる）
                conn.execute(text("DELETE FROM statuses WHERE project_id = :project_id"), {"project_id": project_id})
                
                # 新しいステータスを作成
                for status_data in new_statuses:
                    conn.execute(text("""
                        INSERT INTO statuses (name, display_name, "order", color, project_id)
                        VALUES (:name, :display_name, :order, :color, :project_id)
                    """), {
                        "name": status_data["name"],
                        "display_name": status_data["display_name"],
                        "order": status_data["order"],
                        "color": status_data["color"],
                        "project_id": project_id
                    })
                
                print(f"プロジェクトID {project_id} のステータスを更新しました")
            
            # 既存のタスクのstatusフィールドを新しいステータス名にマッピング
            # 古いステータス名から新しいステータス名へのマッピング
            status_mapping = {
                "todo": "not_started",
                "doing": "in_progress",
                "done": "production_deployed",
                "review": "review_pending"
            }
            
            # 各マッピングを適用
            for old_status, new_status in status_mapping.items():
                conn.execute(text("""
                    UPDATE tasks 
                    SET status = :new_status, status_id = NULL
                    WHERE status = :old_status AND project_id != -1
                """), {"old_status": old_status, "new_status": new_status})
            
            # プロジェクトごとに、新しいstatus_idを設定
            for (project_id,) in projects:
                for status_data in new_statuses:
                    # ステータスIDを取得
                    status_result = conn.execute(text("""
                        SELECT id FROM statuses 
                        WHERE project_id = :project_id AND name = :name
                    """), {"project_id": project_id, "name": status_data["name"]})
                    status_row = status_result.fetchone()
                    
                    if status_row:
                        status_id = status_row[0]
                        # 該当するタスクのstatus_idを更新
                        conn.execute(text("""
                            UPDATE tasks 
                            SET status_id = :status_id
                            WHERE project_id = :project_id AND status = :status_name
                        """), {
                            "status_id": status_id,
                            "project_id": project_id,
                            "status_name": status_data["name"]
                        })
            
            trans.commit()
            print("すべてのプロジェクトのステータスを更新しました")
        except Exception as e:
            trans.rollback()
            print(f"ステータス更新マイグレーションエラー: {e}")
            raise

if __name__ == "__main__":
    migrate()
