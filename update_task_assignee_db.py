#!/usr/bin/env python3
"""
既存のタスクの担当者をデータベースに直接接続して更新するスクリプト
"""
import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor

# データベース接続設定
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "taskapp_db")
DB_USER = os.getenv("DB_USER", "taskapp")
DB_PASSWORD = os.getenv("DB_PASSWORD", "taskapp_password")

def main():
    print("既存のタスクの担当者を h73440 に更新します...")
    print(f"データベース: {DB_HOST}:{DB_PORT}/{DB_NAME}\n")
    
    try:
        # データベース接続
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # 更新前の状態を確認
        cur.execute("SELECT COUNT(*) FROM tasks WHERE assignee != 'h73440' OR assignee IS NULL")
        count_to_update = cur.fetchone()['count']
        print(f"更新対象: {count_to_update} 件のタスク\n")
        
        if count_to_update == 0:
            print("更新するタスクがありません。")
            cur.close()
            conn.close()
            return
        
        # 一括更新
        print("タスクの担当者を更新中...")
        cur.execute(
            "UPDATE tasks SET assignee = 'h73440' WHERE assignee != 'h73440' OR assignee IS NULL"
        )
        updated_count = cur.rowcount
        
        # コミット
        conn.commit()
        cur.close()
        conn.close()
        
        print(f"\n{'='*50}")
        print(f"更新が完了しました！")
        print(f"  更新: {updated_count} 件")
        print(f"  合計: {count_to_update} 件")
        
    except Exception as e:
        print(f"✗ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
