#!/usr/bin/env python3
"""
既存のタスクの担当者を更新するスクリプト
"""
import requests
import sys

API_URL = "http://localhost:8000"
TIMEOUT = 30  # タイムアウトを30秒に設定

def get_all_tasks():
    """すべてのタスクを取得（ページネーション対応）"""
    print("タスク一覧を取得中...")
    url = f"{API_URL}/api/v1/tasks"
    all_tasks = []
    skip = 0
    limit = 100
    
    try:
        while True:
            print(f"  取得中: skip={skip}, limit={limit}")
            response = requests.get(url, params={"skip": skip, "limit": limit}, timeout=TIMEOUT)
            response.raise_for_status()
            tasks = response.json()
            
            if not tasks:
                break
            
            all_tasks.extend(tasks)
            print(f"  → {len(tasks)} 件取得（累計: {len(all_tasks)} 件）")
            
            if len(tasks) < limit:
                break
            
            skip += limit
        
        print(f"✓ 合計 {len(all_tasks)} 件のタスクを取得しました\n")
        return all_tasks
    except requests.exceptions.RequestException as e:
        print(f"✗ タスク取得エラー: {e}")
        sys.exit(1)

def update_task_assignee(task_id: int, assignee: str):
    """タスクの担当者を更新"""
    url = f"{API_URL}/api/v1/tasks/{task_id}"
    data = {"assignee": assignee}
    try:
        response = requests.put(url, json=data, timeout=TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"✗ タスク {task_id} の更新エラー: {e}")
        return None

def main():
    print("既存のタスクの担当者を h73440 に更新します...")
    print(f"API URL: {API_URL}\n")
    
    tasks = get_all_tasks()
    if not tasks:
        print("更新するタスクがありません。")
        return
    
    updated_count = 0
    skipped_count = 0
    error_count = 0
    
    for i, task in enumerate(tasks, 1):
        task_id = task.get("id")
        task_title = task.get("title", "無題")
        current_assignee = task.get("assignee")
        
        print(f"[{i}/{len(tasks)}] タスク ID: {task_id}, タイトル: {task_title}")
        
        if current_assignee == "h73440":
            print(f"  → スキップ（既に h73440 が担当者）")
            skipped_count += 1
            continue
        
        result = update_task_assignee(task_id, "h73440")
        if result:
            updated_count += 1
            print(f"  ✓ 担当者を h73440 に更新しました")
        else:
            error_count += 1
            print(f"  ✗ 更新に失敗しました")
    
    print(f"\n{'='*50}")
    print(f"更新が完了しました！")
    print(f"  更新: {updated_count} 件")
    print(f"  スキップ: {skipped_count} 件")
    print(f"  エラー: {error_count} 件")
    print(f"  合計: {len(tasks)} 件")

if __name__ == "__main__":
    main()
