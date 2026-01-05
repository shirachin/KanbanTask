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
- Git

### 初回セットアップ手順

1. **リポジトリのクローン**

```bash
git clone https://github.com/shirachin/KanbanTask.git
cd KanbanTask
```

2. **環境変数ファイルの作成**

`.env.example`をコピーして`.env`ファイルを作成します：

```bash
cp .env.example .env
```

3. **環境変数の設定（必要に応じて編集）**

`.env`ファイルを開いて、以下の環境変数を設定します：

```env
# デプロイ先のIPアドレス（localhost または サーバーのIPアドレス）
DEPLOY_IP=localhost

# フロントエンドのポート番号
FRONTEND_PORT=5173

# バックエンドのポート番号
BACKEND_PORT=8001

# プロキシ設定（プロキシ環境下でライブラリインストールが必要な場合）
# HTTPプロキシ（例: http://proxy.example.com:8080）
HTTP_PROXY=

# HTTPSプロキシ（例: http://proxy.example.com:8080）
HTTPS_PROXY=

# プロキシを経由しないホスト（カンマ区切り、例: localhost,127.0.0.1,.local）
NO_PROXY=localhost,127.0.0.1,.local
```

**注意**: 
- 他のマシンからアクセスする場合は、`DEPLOY_IP`をサーバーのIPアドレスに変更してください
- ポート番号が既に使用されている場合は、別のポート番号に変更してください
- プロキシ環境下でライブラリのインストールに失敗する場合は、`HTTP_PROXY`と`HTTPS_PROXY`を設定してください
- **Dockerネットワークによる分離**: このアプリは独自のDockerネットワーク（`taskapp_network`）を使用するため、他のアプリのPostgreSQLコンテナと同時に動かしてもネットワークレベルで分離されます
- **データベースのポート公開**: デフォルトではデータベースのポートはホスト側に公開されていません（バックエンドコンテナからは`db:5432`でアクセス可能）。外部から直接アクセスする必要がある場合は、`docker-compose.yml`の`db`サービスの`ports`セクションのコメントを外してください

4. **アプリケーションの起動**

```bash
docker-compose up --build
```

初回起動時は、Dockerイメージのビルドとデータベースの初期化に時間がかかります。

5. **アプリケーションにアクセス**

起動が完了したら、以下のURLにアクセスできます：

- フロントエンド: http://localhost:5173（または http://${DEPLOY_IP}:${FRONTEND_PORT}）
- バックエンドAPI: http://localhost:8001（または http://${DEPLOY_IP}:${BACKEND_PORT}）
- APIドキュメント: http://localhost:8001/docs（または http://${DEPLOY_IP}:${BACKEND_PORT}/docs）

### 停止方法

```bash
docker-compose down
```

データベースのデータも削除する場合：

```bash
docker-compose down -v
```

## API エンドポイント

APIは `/api/v1` プレフィックスで提供されています。

### タスク管理
- `GET /api/v1/tasks` - タスク一覧を取得
- `GET /api/v1/tasks/{task_id}` - 特定のタスクを取得
- `POST /api/v1/tasks` - 新しいタスクを作成
- `PUT /api/v1/tasks/{task_id}` - タスクを更新
- `DELETE /api/v1/tasks/{task_id}` - タスクを削除
- `GET /api/v1/tasks/{task_id}/todos` - タスクのTODO一覧を取得
- `POST /api/v1/tasks/{task_id}/todos` - タスクにTODOを追加

### プロジェクト管理
- `GET /api/v1/projects` - プロジェクト一覧を取得
- `GET /api/v1/projects/{project_id}` - 特定のプロジェクトを取得
- `POST /api/v1/projects` - 新しいプロジェクトを作成
- `PUT /api/v1/projects/{project_id}` - プロジェクトを更新
- `DELETE /api/v1/projects/{project_id}` - プロジェクトを削除

### ステータス管理
- `GET /api/v1/statuses` - ステータス一覧を取得
- `POST /api/v1/statuses` - 新しいステータスを作成
- `PUT /api/v1/statuses/{status_id}` - ステータスを更新
- `DELETE /api/v1/statuses/{status_id}` - ステータスを削除

### TODO管理
- `GET /api/v1/todos` - TODO一覧を取得
- `PUT /api/v1/todos/{todo_id}` - TODOを更新
- `DELETE /api/v1/todos/{todo_id}` - TODOを削除

詳細はAPIドキュメント（http://localhost:8001/docs）を参照してください。

## プロジェクト構造

```
taskapp/
├── backend/                    # FastAPIバックエンド
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py            # アプリケーションエントリーポイント
│       ├── core/              # コア機能
│       │   ├── config.py      # 設定管理
│       │   ├── database.py    # データベース接続
│       │   ├── exceptions.py  # 例外ハンドラー
│       │   └── ...
│       ├── models/            # データモデル
│       ├── schemas/           # Pydanticスキーマ
│       ├── api/               # APIルーター
│       │   └── v1/
│       └── migrations/        # データベースマイグレーション
├── frontend/                  # Vue.jsフロントエンド
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── views/            # ページコンポーネント
│       ├── components/       # 共通コンポーネント
│       ├── composables/      # コンポジション関数
│       └── ...
├── data/                      # データディレクトリ（データベースデータ）
│   └── postgres/
├── docker-compose.yml
├── .env.example              # 環境変数のサンプル
└── README.md
```

## 開発

### バックエンドの開発

バックエンドのコードを変更すると、自動的にリロードされます（ホットリロード有効）。

### フロントエンドの開発

フロントエンドのコードを変更すると、自動的にリロードされます（Viteのホットリロード有効）。

## データベース

PostgreSQLデータベースは自動的に初期化され、必要なテーブルが作成されます。

### Dockerネットワーク経由での接続（推奨）

バックエンドコンテナからは、Dockerネットワーク経由で`db:5432`にアクセスします。デフォルトでは、データベースのポートはホスト側に公開されていません。

データベース接続情報（コンテナ内から）：
- ホスト: `db` (Dockerネットワーク内のサービス名)
- ポート: `5432` (コンテナ内のポート)
- データベース名: `.env`ファイルの`DB_NAME`で設定（デフォルト: `taskapp_db`）
- ユーザー名: `.env`ファイルの`DB_USER`で設定（デフォルト: `taskapp`）
- パスワード: `.env`ファイルの`DB_PASSWORD`で設定（デフォルト: `taskapp_password`）

### 外部から直接アクセスする場合

外部から直接データベースにアクセスする必要がある場合は、`docker-compose.yml`の`db`サービスの`ports`セクションのコメントを外してください：

```yaml
ports:
  - "${DB_PORT:-5432}:5432"
```

その後、以下の情報でアクセスできます：
- ホスト: `localhost` または `.env`ファイルの`DEPLOY_IP`
- ポート: `.env`ファイルの`DB_PORT`で設定（デフォルト: `5432`）

### 外部のPostgreSQLコンテナと接続する場合

他のDocker ComposeプロジェクトのPostgreSQLコンテナと接続する場合：

1. 外部ネットワークを作成（または既存のネットワークを使用）：
```bash
docker network create shared_db_network
```

2. `docker-compose.yml`に外部ネットワークを追加：
```yaml
networks:
  taskapp_network:
    driver: bridge
  external_db_network:
    external: true
    name: shared_db_network
```

3. `db`サービスと`backend`サービスに外部ネットワークを追加：
```yaml
services:
  db:
    networks:
      - taskapp_network
      - external_db_network
  backend:
    networks:
      - taskapp_network
      - external_db_network
```

**注意**: 
- 本番環境では、データベースのパスワードを変更してください
- Dockerネットワークにより、他のアプリのPostgreSQLコンテナと同時に動かしてもネットワークレベルで分離されます

## トラブルシューティング

### ポートが既に使用されている場合

`.env`ファイルでポート番号を変更してください：

```env
FRONTEND_PORT=5174
BACKEND_PORT=8002
```

### データベースのリセット

データベースを完全にリセットする場合：

```bash
docker-compose down -v
docker-compose up --build
```

### ログの確認

各サービスのログを確認する場合：

```bash
# すべてのサービスのログ
docker-compose logs

# 特定のサービスのログ
docker-compose logs backend
docker-compose logs frontend
docker-compose logs db
```

### コンテナの再ビルド

コードを変更した後、コンテナを再ビルドする場合：

```bash
docker-compose up --build
```

## バージョン情報

現在のバージョン: **β0.1.0**

リリースノートは、アプリケーション内の「更新情報」ページで確認できます。
