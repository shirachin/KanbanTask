"""
既存のデータベースにprojectsテーブルを追加し、tasksとstatusesにproject_idを追加するマイグレーションスクリプト
"""
from sqlalchemy import create_engine, text
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://taskapp:taskapp_password@db:5432/taskapp_db")

def migrate():
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            # projectsテーブルが存在するか確認
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name='projects'
            """))
            
            project_exists = result.fetchone() is not None
            
            if not project_exists:
                print("projectsテーブルを作成しています...")
                conn.execute(text("""
                    CREATE TABLE projects (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR NOT NULL,
                        description VARCHAR,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP WITH TIME ZONE
                    )
                """))
                
                # デフォルトプロジェクトを作成
                result = conn.execute(text("""
                    INSERT INTO projects (name, description) 
                    VALUES ('デフォルトプロジェクト', 'デフォルトのプロジェクト')
                    RETURNING id
                """))
                default_project_id = result.fetchone()[0]
                print(f"デフォルトプロジェクトを作成しました (ID: {default_project_id})")
            else:
                # 既存のプロジェクトから最初のプロジェクトを取得
                result = conn.execute(text("""
                    SELECT id FROM projects ORDER BY id LIMIT 1
                """))
                row = result.fetchone()
                if row:
                    default_project_id = row[0]
                    print(f"既存のプロジェクトを使用します (ID: {default_project_id})")
                else:
                    # プロジェクトが存在しない場合は作成
                    result = conn.execute(text("""
                        INSERT INTO projects (name, description) 
                        VALUES ('デフォルトプロジェクト', 'デフォルトのプロジェクト')
                        RETURNING id
                    """))
                    default_project_id = result.fetchone()[0]
                    print(f"デフォルトプロジェクトを作成しました (ID: {default_project_id})")
            
            # statusesテーブルにproject_idカラムを追加
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='statuses' AND column_name='project_id'
            """))
            
            if result.fetchone() is None:
                print("statusesテーブルにproject_idカラムを追加しています...")
                conn.execute(text("""
                    ALTER TABLE statuses 
                    ADD COLUMN project_id INTEGER
                """))
                
                # 既存のstatusesにデフォルトプロジェクトIDを設定
                conn.execute(text("""
                    UPDATE statuses 
                    SET project_id = :project_id
                    WHERE project_id IS NULL
                """), {"project_id": default_project_id})
                
                # NOT NULL制約を追加
                conn.execute(text("""
                    ALTER TABLE statuses 
                    ALTER COLUMN project_id SET NOT NULL
                """))
                
                # 外部キー制約を追加
                try:
                    conn.execute(text("""
                        ALTER TABLE statuses 
                        ADD CONSTRAINT fk_statuses_project 
                        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
                    """))
                except Exception as e:
                    print(f"外部キー制約の追加をスキップ（既に存在する可能性）: {e}")
                
                # statusesのunique制約を削除して、project_idとnameの組み合わせでuniqueにする
                try:
                    conn.execute(text("""
                        ALTER TABLE statuses 
                        DROP CONSTRAINT IF EXISTS statuses_name_key
                    """))
                except:
                    pass
                
                try:
                    conn.execute(text("""
                        CREATE UNIQUE INDEX IF NOT EXISTS statuses_project_name_unique 
                        ON statuses(project_id, name)
                    """))
                except Exception as e:
                    print(f"ユニークインデックスの作成をスキップ（既に存在する可能性）: {e}")
            
            # tasksテーブルにproject_idカラムを追加
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='tasks' AND column_name='project_id'
            """))
            
            if result.fetchone() is None:
                print("tasksテーブルにproject_idカラムを追加しています...")
                conn.execute(text("""
                    ALTER TABLE tasks 
                    ADD COLUMN project_id INTEGER
                """))
                
                # 既存のtasksにデフォルトプロジェクトIDを設定
                conn.execute(text("""
                    UPDATE tasks 
                    SET project_id = :project_id
                    WHERE project_id IS NULL
                """), {"project_id": default_project_id})
                
                # NOT NULL制約を追加
                conn.execute(text("""
                    ALTER TABLE tasks 
                    ALTER COLUMN project_id SET NOT NULL
                """))
                
                # 外部キー制約を追加
                try:
                    conn.execute(text("""
                        ALTER TABLE tasks 
                        ADD CONSTRAINT fk_tasks_project 
                        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
                    """))
                except Exception as e:
                    print(f"外部キー制約の追加をスキップ（既に存在する可能性）: {e}")
            
            trans.commit()
            print("マイグレーションが完了しました！")
        except Exception as e:
            trans.rollback()
            print(f"エラーが発生しました: {e}")
            raise

if __name__ == "__main__":
    migrate()
