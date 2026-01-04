# HTTPステータスコードとエラーメッセージ一覧

このドキュメントは、APIで使用されるHTTPステータスコードとエラーメッセージの一覧です。

## 成功レスポンス

- **200 OK**: リクエストが正常に処理された
  - GET: リソースの取得
  - PUT: リソースの更新
  - POST: リソースの作成（一部）

- **201 Created**: リソースが正常に作成された
  - POST: リソースの作成

## クライアントエラー

- **400 Bad Request**: リクエストが不正
  - バリデーションエラー（Pydanticスキーマ）
  - データベース制約違反（IntegrityError）
  - 必須フィールドの欠如
  - ビジネスロジックエラー（例：個人タスクに担当者が指定されていない）

- **403 Forbidden**: リソースへのアクセスが禁止されている
  - システムプロジェクト（id=-1）の更新・削除

- **404 Not Found**: リソースが見つからない
  - 存在しないIDでのリソース取得
  - 存在しないIDでのリソース更新・削除

- **422 Unprocessable Entity**: リクエストの形式は正しいが、処理できない
  - FastAPIのバリデーションエラー（RequestValidationError）

## サーバーエラー

- **500 Internal Server Error**: サーバー内部エラー
  - 予期しない例外
  - データベースエラー（SQLAlchemyError、IntegrityError以外）
  - その他のシステムエラー

## エラーメッセージ

### 404 Not Found
- `"Task with id {task_id} not found"`
- `"Project with id {project_id} not found"`
- `"Status with id {status_id} not found"`
- `"Todo with id {todo_id} not found"`

### 400 Bad Request
- `"Assignee is required for personal tasks"` - 個人タスクに担当者が指定されていない
- `"Status with this name already exists in this project"` - ステータス名の重複
- `"Cannot create {resource} due to database constraints"` - データベース制約違反（作成時）
- `"Cannot update {resource} due to database constraints"` - データベース制約違反（更新時）
- `"Cannot delete {resource} due to related data constraints"` - 関連データがあるため削除不可
- `"Cannot perform this operation due to related data constraints"` - 関連データ制約違反（グローバルハンドラー）
- `"A record with this value already exists"` - ユニーク制約違反（グローバルハンドラー）
- `"Required field is missing"` - NOT NULL制約違反（グローバルハンドラー）
- `"Database constraint violation"` - その他のデータベース制約違反（グローバルハンドラー）

### 403 Forbidden
- `"Cannot update system project"` - システムプロジェクトの更新禁止
- `"Cannot delete system project"` - システムプロジェクトの削除禁止

### 422 Unprocessable Entity
- FastAPIのバリデーションエラーの詳細（`exc.errors()`）

### 500 Internal Server Error
- `"Database error occurred"` - データベースエラー
- `"Error fetching statuses"` - ステータス取得エラー
- `"Internal server error"` - その他の予期しないエラー

## エラーハンドリングの流れ

1. **エンドポイント内でのエラーハンドリング**
   - `IntegrityError`: `HTTPException(status_code=400)`をraise（具体的なメッセージ付き）
   - `SQLAlchemyError`: `HTTPException(status_code=500)`をraise
   - リソース未存在: `HTTPException(status_code=404)`をraise（IDを含むメッセージ）
   - ビジネスロジックエラー: `HTTPException(status_code=400)`をraise（具体的なメッセージ）

2. **グローバル例外ハンドラー**
   - `HTTPException`: そのまま返す（CORSヘッダーを追加）
   - `RequestValidationError`: `422`を返す（バリデーションエラーの詳細）
   - `IntegrityError`: `400`を返す（ユーザーフレンドリーなメッセージに変換）
   - `SQLAlchemyError`: `500`を返す（エンドポイントでキャッチされなかった場合）
   - その他の例外: `500`を返す（ログに詳細を記録）
