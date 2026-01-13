#!/usr/bin/env python3
"""
テスト用のタスクとTODOを作成するスクリプト
すべてのカラムにデータが入るように作成
"""
import requests
import json
from datetime import datetime, date, timedelta

API_URL = "http://localhost:8001"

def create_task(title: str, project_id: int = -1, assignee: str = "h73440", description: str = None):
    """タスクを作成"""
    url = f"{API_URL}/api/v1/tasks"
    data = {
        "title": title,
        "project_id": project_id,
        "assignee": assignee,
        "description": description,
        "status": "未着手"
    }
    response = requests.post(url, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error creating task: {response.status_code} - {response.text}")
        return None

def create_todo(task_id: int, title: str, completed: bool = False, scheduled_date: str = None, completed_date: str = None, order: int = 0):
    """TODOを作成"""
    url = f"{API_URL}/api/v1/tasks/{task_id}/todos"
    data = {
        "task_id": task_id,
        "title": title,
        "completed": completed,
        "order": order
    }
    if scheduled_date:
        data["scheduled_date"] = scheduled_date
    if completed_date:
        data["completed_date"] = completed_date
    
    response = requests.post(url, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error creating todo: {response.status_code} - {response.text}")
        return None

def update_todo(todo_id: int, completed: bool = None, completed_date: str = None):
    """TODOを更新"""
    url = f"{API_URL}/api/v1/todos/{todo_id}"
    data = {}
    if completed is not None:
        data["completed"] = completed
    if completed_date:
        data["completed_date"] = completed_date
    
    if data:
        response = requests.put(url, json=data)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error updating todo: {response.status_code} - {response.text}")
    return None

def get_projects():
    """プロジェクト一覧を取得"""
    url = f"{API_URL}/api/v1/projects"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("items", [])
    return []

def main():
    print("テスト用のタスクとTODOを作成します...")
    
    # プロジェクトを取得
    projects = get_projects()
    project_ids = [p["id"] for p in projects[:3]] if projects else []
    
    # 日付を計算（今日から過去・未来）
    today = date.today()
    
    # 個人タスク（project_id=-1）を作成
    personal_tasks = [
        ("朝のルーティン", "毎日の朝のタスク", [
            ("起床", True, (today - timedelta(days=1)).isoformat(), (today - timedelta(days=1)).isoformat(), 0),
            ("朝食", True, (today - timedelta(days=1)).isoformat(), (today - timedelta(days=1)).isoformat(), 1),
            ("運動", False, today.isoformat(), None, 2),
            ("読書", False, (today + timedelta(days=1)).isoformat(), None, 3),
        ]),
        ("仕事のタスク", "仕事関連のタスク", [
            ("メール確認", True, (today - timedelta(days=2)).isoformat(), (today - timedelta(days=2)).isoformat(), 0),
            ("会議準備", True, (today - timedelta(days=1)).isoformat(), (today - timedelta(days=1)).isoformat(), 1),
            ("資料作成", False, today.isoformat(), None, 2),
            ("報告書作成", False, (today + timedelta(days=1)).isoformat(), None, 3),
            ("来週の計画", False, (today + timedelta(days=3)).isoformat(), None, 4),
        ]),
        ("買い物リスト", "買い物関連のタスク", [
            ("野菜を買う", True, (today - timedelta(days=3)).isoformat(), (today - timedelta(days=3)).isoformat(), 0),
            ("肉を買う", True, (today - timedelta(days=2)).isoformat(), (today - timedelta(days=2)).isoformat(), 1),
            ("調味料を買う", False, today.isoformat(), None, 2),
            ("日用品を買う", False, (today + timedelta(days=2)).isoformat(), None, 3),
        ]),
        ("学習タスク", "学習関連のタスク", [
            ("Python学習", True, (today - timedelta(days=5)).isoformat(), (today - timedelta(days=5)).isoformat(), 0),
            ("Vue.js学習", True, (today - timedelta(days=3)).isoformat(), (today - timedelta(days=3)).isoformat(), 1),
            ("TypeScript学習", False, today.isoformat(), None, 2),
            ("データベース学習", False, (today + timedelta(days=2)).isoformat(), None, 3),
            ("アルゴリズム学習", False, (today + timedelta(days=5)).isoformat(), None, 4),
        ]),
        ("健康管理", "健康関連のタスク", [
            ("健康診断", True, (today - timedelta(days=10)).isoformat(), (today - timedelta(days=10)).isoformat(), 0),
            ("運動", False, today.isoformat(), None, 1),
            ("ストレッチ", False, (today + timedelta(days=1)).isoformat(), None, 2),
        ]),
    ]
    
    for task_title, task_desc, todos in personal_tasks:
        task = create_task(task_title, project_id=-1, description=task_desc)
        if task:
            print(f"✓ タスク作成: {task['title']} (ID: {task['id']})")
            for todo_title, completed, scheduled_date, completed_date, order in todos:
                todo = create_todo(task['id'], todo_title, completed, scheduled_date, completed_date, order)
                if todo:
                    print(f"  ✓ TODO作成: {todo['title']} (completed={completed}, scheduled={scheduled_date}, completed_date={completed_date})")
    
    # プロジェクトに紐づくタスクを作成
    if project_ids:
        project_tasks = [
            ("UIデザイン", "ユーザーインターフェースのデザイン", [
                ("ワイヤーフレーム作成", True, (today - timedelta(days=7)).isoformat(), (today - timedelta(days=7)).isoformat(), 0),
                ("モックアップ作成", True, (today - timedelta(days=5)).isoformat(), (today - timedelta(days=5)).isoformat(), 1),
                ("デザインシステム構築", False, today.isoformat(), None, 2),
                ("コンポーネント設計", False, (today + timedelta(days=2)).isoformat(), None, 3),
            ]),
            ("API開発", "RESTful APIの開発", [
                ("エンドポイント設計", True, (today - timedelta(days=6)).isoformat(), (today - timedelta(days=6)).isoformat(), 0),
                ("認証機能実装", True, (today - timedelta(days=4)).isoformat(), (today - timedelta(days=4)).isoformat(), 1),
                ("データベース設計", False, today.isoformat(), None, 2),
                ("エラーハンドリング", False, (today + timedelta(days=1)).isoformat(), None, 3),
                ("テスト作成", False, (today + timedelta(days=3)).isoformat(), None, 4),
            ]),
            ("フロントエンド開発", "Vue.jsを使用したフロントエンド開発", [
                ("コンポーネント実装", True, (today - timedelta(days=8)).isoformat(), (today - timedelta(days=8)).isoformat(), 0),
                ("状態管理実装", True, (today - timedelta(days=6)).isoformat(), (today - timedelta(days=6)).isoformat(), 1),
                ("ルーティング設定", False, today.isoformat(), None, 2),
                ("API連携", False, (today + timedelta(days=1)).isoformat(), None, 3),
                ("スタイリング", False, (today + timedelta(days=4)).isoformat(), None, 4),
            ]),
            ("テスト", "ユニットテストと統合テスト", [
                ("ユニットテスト作成", True, (today - timedelta(days=9)).isoformat(), (today - timedelta(days=9)).isoformat(), 0),
                ("統合テスト作成", False, today.isoformat(), None, 1),
                ("E2Eテスト作成", False, (today + timedelta(days=2)).isoformat(), None, 2),
            ]),
            ("デプロイ", "本番環境へのデプロイ", [
                ("ステージング環境デプロイ", True, (today - timedelta(days=2)).isoformat(), (today - timedelta(days=2)).isoformat(), 0),
                ("本番環境デプロイ", False, (today + timedelta(days=1)).isoformat(), None, 1),
            ]),
        ]
        
        for i, (task_title, task_desc, todos) in enumerate(project_tasks):
            project_id = project_ids[i % len(project_ids)]
            task = create_task(task_title, project_id=project_id, description=task_desc)
            if task:
                print(f"✓ タスク作成: {task['title']} (Project ID: {project_id}, Task ID: {task['id']})")
                for todo_title, completed, scheduled_date, completed_date, order in todos:
                    todo = create_todo(task['id'], todo_title, completed, scheduled_date, completed_date, order)
                    if todo:
                        print(f"  ✓ TODO作成: {todo['title']} (completed={completed}, scheduled={scheduled_date}, completed_date={completed_date})")
    
    # さらに多くのタスクを作成（データ量を増やすため）
    additional_tasks = [
        ("バグ修正", "既存のバグを修正", [
            ("バグ調査", True, (today - timedelta(days=4)).isoformat(), (today - timedelta(days=4)).isoformat(), 0),
            ("修正実装", True, (today - timedelta(days=2)).isoformat(), (today - timedelta(days=2)).isoformat(), 1),
            ("テスト", False, today.isoformat(), None, 2),
        ]),
        ("パフォーマンス改善", "アプリケーションのパフォーマンス改善", [
            ("ボトルネック調査", True, (today - timedelta(days=6)).isoformat(), (today - timedelta(days=6)).isoformat(), 0),
            ("最適化実装", False, today.isoformat(), None, 1),
            ("ベンチマーク", False, (today + timedelta(days=2)).isoformat(), None, 2),
        ]),
        ("セキュリティ対策", "セキュリティ対策の実装", [
            ("脆弱性調査", True, (today - timedelta(days=7)).isoformat(), (today - timedelta(days=7)).isoformat(), 0),
            ("対策実装", False, today.isoformat(), None, 1),
            ("セキュリティテスト", False, (today + timedelta(days=3)).isoformat(), None, 2),
        ]),
        ("ドキュメント作成", "技術ドキュメントの作成", [
            ("API仕様書", True, (today - timedelta(days=5)).isoformat(), (today - timedelta(days=5)).isoformat(), 0),
            ("ユーザーマニュアル", False, today.isoformat(), None, 1),
            ("開発ガイド", False, (today + timedelta(days=4)).isoformat(), None, 2),
        ]),
        ("コードレビュー", "コードレビューの実施", [
            ("レビュー依頼", True, (today - timedelta(days=3)).isoformat(), (today - timedelta(days=3)).isoformat(), 0),
            ("レビュー実施", False, today.isoformat(), None, 1),
            ("修正対応", False, (today + timedelta(days=1)).isoformat(), None, 2),
        ]),
    ]
    
    for task_title, task_desc, todos in additional_tasks:
        task = create_task(task_title, project_id=-1, description=task_desc)
        if task:
            print(f"✓ タスク作成: {task['title']} (ID: {task['id']})")
            for todo_title, completed, scheduled_date, completed_date, order in todos:
                todo = create_todo(task['id'], todo_title, completed, scheduled_date, completed_date, order)
                if todo:
                    print(f"  ✓ TODO作成: {todo['title']} (completed={completed}, scheduled={scheduled_date}, completed_date={completed_date})")
    
    print("\nテストデータの作成が完了しました！")
    print(f"合計: タスク約{len(personal_tasks) + len(additional_tasks) + (len(project_tasks) if project_ids else 0)}件、TODO約{sum(len(todos) for _, _, todos in personal_tasks) + sum(len(todos) for _, _, todos in additional_tasks) + (sum(len(todos) for _, _, todos in project_tasks) if project_ids else 0)}件")

if __name__ == "__main__":
    main()
