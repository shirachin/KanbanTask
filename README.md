# タスク管理アプリ

Dockerを使用したPython（FastAPI）+ Vue.js + PostgreSQLのタスク管理アプリケーションです。

## 構成

- **バックエンド**: FastAPI (Python 3.11)
- **フロントエンド**: Vue.js 3 + Vite
- **データベース**: PostgreSQL 15

## セットアップ

### 前提条件

- Docker
- Docker Compose

### 起動方法

1. プロジェクトのルートディレクトリで以下のコマンドを実行：

```bash
docker-compose up --build
```

2. アプリケーションにアクセス：
   - フロントエンド: http://localhost:5173
   - バックエンドAPI: http://localhost:8001
   - APIドキュメント: http://localhost:8001/docs

### 停止方法

```bash
docker-compose down
```

データベースのデータも削除する場合：

```bash
docker-compose down -v
```

## API エンドポイント

- `GET /api/tasks` - タスク一覧を取得
- `GET /api/tasks/{task_id}` - 特定のタスクを取得
- `POST /api/tasks` - 新しいタスクを作成
- `PUT /api/tasks/{task_id}` - タスクを更新
- `DELETE /api/tasks/{task_id}` - タスクを削除

## プロジェクト構造

```
taskapp/
├── backend/          # FastAPIバックエンド
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py       # APIエンドポイント
│   ├── models.py     # データベースモデル
│   ├── schemas.py    # Pydanticスキーマ
│   └── database.py   # データベース接続設定
├── frontend/         # Vue.jsフロントエンド
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   └── src/
│       ├── main.js
│       └── App.vue
├── docker-compose.yml
└── README.md
```

## 開発

### バックエンドの開発

バックエンドのコードを変更すると、自動的にリロードされます（ホットリロード有効）。

### フロントエンドの開発

フロントエンドのコードを変更すると、自動的にリロードされます（Viteのホットリロード有効）。

## データベース

PostgreSQLデータベースは自動的に初期化され、`tasks`テーブルが作成されます。

データベース接続情報：
- ホスト: `db` (Docker内部)
- ポート: `5432`
- データベース名: `taskapp_db`
- ユーザー名: `taskapp`
- パスワード: `taskapp_password`
