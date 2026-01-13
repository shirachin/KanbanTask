# エンドポイント一覧

## 現在実装済み

### Task (`/api/v1/tasks`)

タスク管理機能。プロジェクトに紐づくタスクや個人タスク（project_id=-1）を管理します。

- `GET /api/v1/tasks` - タスク一覧取得
  - クエリパラメータ: `project_id`, `project_ids`, `assignee`, `skip`, `limit`
  - フィルタリング、ページネーション対応
- `GET /api/v1/tasks/{task_id}` - タスク詳細取得
- `POST /api/v1/tasks` - タスク作成
  - 個人タスク（project_id=-1）の場合は`assignee`が必須
- `PUT /api/v1/tasks/{task_id}` - タスク更新
- `PUT /api/v1/tasks/{task_id}/order` - タスク順序更新
  - 同じステータス内でのタスクの順序を変更
- `DELETE /api/v1/tasks/{task_id}` - タスク削除
  - 関連するTODOもカスケード削除
- `GET /api/v1/tasks/{task_id}/todos` - タスクに紐づくTODO一覧取得
- `POST /api/v1/tasks/{task_id}/todos` - タスクにTODO作成

### Project (`/api/v1/projects`)

プロジェクト管理機能。プロジェクトのCRUD操作とフィルタリング機能を提供します。

- `GET /api/v1/projects` - プロジェクト一覧取得
  - クエリパラメータ: `assignee`, `name`, `start_month`, `end_month`, `skip`, `limit`, `sort_by`, `sort_order`
  - フィルタリング、ソート、ページネーション対応
  - システムプロジェクト（id=-1）は除外
- `GET /api/v1/projects/{project_id}` - プロジェクト詳細取得
- `POST /api/v1/projects` - プロジェクト作成
  - ステータスは共通化されているため、プロジェクト作成時にステータスは作成されない
- `PUT /api/v1/projects/{project_id}` - プロジェクト更新
  - システムプロジェクト（id=-1）は更新不可
- `DELETE /api/v1/projects/{project_id}` - プロジェクト削除
  - システムプロジェクト（id=-1）は削除不可
  - 関連するタスクもカスケード削除

### Status (`/api/v1/statuses`)

ステータス管理機能（共通リソース）。すべてのプロジェクトと個人タスクで共有される共通ステータスを管理します。

- `GET /api/v1/statuses` - ステータス一覧取得
  - 共通ステータス（project_id IS NULL）を取得
  - クエリパラメータ: `project_id`（現在は未使用）
- `POST /api/v1/statuses` - ステータス作成
  - ステータス名は同一プロジェクト内で一意である必要がある
- `PUT /api/v1/statuses/{status_id}` - ステータス更新
- `DELETE /api/v1/statuses/{status_id}` - ステータス削除
  - このステータスを使用しているタスクがある場合は削除不可

### Todo (`/api/v1/todos`)

TODO管理機能。タスクに紐づくTODOアイテムを管理します。

- `GET /api/v1/todos` - TODO一覧取得
  - クエリパラメータ: `skip`, `limit`, `sort_by`, `sort_order`, `title`, `completed`, `task_name`, `project_name`
  - フィルタリング、ソート、ページネーション対応
  - タスク情報とプロジェクト情報を含む
- `PUT /api/v1/todos/{todo_id}` - TODO更新
  - `completed_date`が設定されると自動的に`completed`が`true`になる
- `DELETE /api/v1/todos/{todo_id}` - TODO削除

**注意**: TODOの作成は`POST /api/v1/tasks/{task_id}/todos`を使用します。

## 将来実装予定

### Auth (`/api/v1/auth`)

認証・認可機能。ユーザーのログイン、ログアウト、トークン管理などを提供します。

- ログイン/ログアウト
- トークン管理（JWT等）
- パスワードリセット
- 認証ミドルウェア

### User (`/api/v1/users`)

ユーザー管理機能。ユーザー情報のCRUD操作を提供します。

- ユーザー一覧取得
- ユーザー詳細取得
- ユーザー作成
- ユーザー更新
- ユーザー削除
- プロフィール管理

### Notification (`/api/v1/notifications`)

通知機能。タスクやプロジェクトに関する通知を管理します。

- 通知一覧取得
- 通知作成
- 通知更新（既読状態など）
- 通知削除
- 通知設定

### File/Attachment (`/api/v1/files`)

ファイル添付機能。タスクやプロジェクトにファイルを添付できます。

- ファイルアップロード
- ファイル一覧取得
- ファイルダウンロード
- ファイル削除
- ファイル情報取得

### Comment (`/api/v1/comments`)

コメント機能。タスクやプロジェクトにコメントを追加できます。

- コメント一覧取得
- コメント作成
- コメント更新
- コメント削除
- コメントへの返信

### Search (`/api/v1/search`)

検索機能。タスク、プロジェクト、TODOなどを横断的に検索します。

- 全文検索
- 高度なフィルタリング
- 検索結果のソート
- 検索履歴

### Analytics/Reports (`/api/v1/analytics`)

統計・レポート機能。タスクやプロジェクトの進捗状況を分析します。

- タスク進捗統計
- プロジェクト進捗レポート
- ユーザー別作業量統計
- 期間別レポート
- カスタムレポート生成
