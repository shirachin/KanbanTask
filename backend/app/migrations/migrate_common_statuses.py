"""
ステータスを共通化するマイグレーション
すべてのプロジェクト・個人タスクで共通の7種類のステータスのみを使用するように変更
"""

from sqlalchemy import text

from app.core.constants import DEFAULT_STATUS_DEFINITIONS
from app.core.database import engine


def migrate():
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            # 1. 既存のタスクのstatus_idとstatus名のマッピングを取得
            tasks_result = conn.execute(
                text("""
                SELECT DISTINCT t.id, t.status_id, t.status, t.project_id
                FROM tasks t
                WHERE t.status_id IS NOT NULL
            """)
            )
            tasks = tasks_result.fetchall()

            # 2. 既存のすべてのステータスを削除
            conn.execute(text("DELETE FROM statuses"))

            # 3. project_idをnullable=Trueに変更（既にNULLを許可する場合はスキップ）
            try:
                conn.execute(text("ALTER TABLE statuses ALTER COLUMN project_id DROP NOT NULL"))
            except Exception as e:
                # 既にnullableの場合はスキップ
                print(f"project_idカラムの変更をスキップ（既にnullableの可能性）: {e}")

            # 4. 共通の7つのステータスを作成（project_id=NULL）
            status_id_map = {}  # 古いstatus_id -> 新しいstatus_idのマッピング
            for _idx, status_data in enumerate(DEFAULT_STATUS_DEFINITIONS):
                result = conn.execute(
                    text("""
                    INSERT INTO statuses (name, display_name, "order", color, project_id, created_at)
                    VALUES (:name, :display_name, :order, :color, NULL, NOW())
                    RETURNING id
                """),
                    {
                        "name": status_data["name"],
                        "display_name": status_data["display_name"],
                        "order": status_data["order"],
                        "color": status_data["color"],
                    },
                )
                new_status_id = result.fetchone()[0]

                # status名から新しいIDへのマッピングを作成
                status_id_map[status_data["name"]] = new_status_id

            # 5. タスクのstatus_idを新しい共通ステータスIDに更新
            # status名に基づいてマッピング
            for task_id, _old_status_id, status_name, _project_id in tasks:
                if status_name in status_id_map:
                    new_status_id = status_id_map[status_name]
                    conn.execute(
                        text("""
                        UPDATE tasks
                        SET status_id = :new_status_id
                        WHERE id = :task_id
                    """),
                        {"new_status_id": new_status_id, "task_id": task_id},
                    )

            # 6. status名のみでstatus_idがNULLのタスクも更新
            for status_name, new_status_id in status_id_map.items():
                conn.execute(
                    text("""
                    UPDATE tasks
                    SET status_id = :new_status_id
                    WHERE status = :status_name AND status_id IS NULL
                """),
                    {"new_status_id": new_status_id, "status_name": status_name},
                )

            trans.commit()
            print("ステータス共通化マイグレーションが完了しました")
            print(f"作成された共通ステータス数: {len(status_id_map)}")
        except Exception as e:
            trans.rollback()
            print(f"マイグレーションエラー: {e}")
            raise


if __name__ == "__main__":
    migrate()
