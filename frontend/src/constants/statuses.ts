/**
 * デフォルトステータス定義
 */

export interface DefaultStatus {
  id: number
  name: string
  display_name: string
  order: number
  color: string
  project_id: number
}

/**
 * 共通ステータスのフォールバック用定義（APIから取得できない場合に使用）
 * すべてのプロジェクト・個人タスクで共通の7種類のステータス
 */
export const DEFAULT_PERSONAL_STATUSES: DefaultStatus[] = [
  { id: -1, name: 'considering', display_name: '検討中', order: 0, color: '#9e9e9e', project_id: -1 },
  { id: -2, name: 'not_started', display_name: '未実行', order: 1, color: '#667eea', project_id: -1 },
  { id: -3, name: 'in_progress', display_name: '実行中', order: 2, color: '#ffa726', project_id: -1 },
  { id: -4, name: 'review_pending', display_name: 'レビュー待ち', order: 3, color: '#9c27b0', project_id: -1 },
  { id: -5, name: 'staging_deployed', display_name: '検証環境反映済み', order: 4, color: '#ffeb3b', project_id: -1 },
  { id: -6, name: 'production_deployed', display_name: '本番環境反映済み', order: 5, color: '#51cf66', project_id: -1 },
  { id: -7, name: 'cancelled', display_name: '中止', order: 6, color: '#dc3545', project_id: -1 },
]

/**
 * プロジェクト用のデフォルトステータス定義（project_idは後で設定）
 */
export const DEFAULT_STATUS_DEFINITIONS = [
  { name: 'considering', display_name: '検討中', order: 0, color: '#9e9e9e' },
  { name: 'not_started', display_name: '未実行', order: 1, color: '#667eea' },
  { name: 'in_progress', display_name: '実行中', order: 2, color: '#ffa726' },
  { name: 'review_pending', display_name: 'レビュー待ち', order: 3, color: '#9c27b0' },
  { name: 'staging_deployed', display_name: '検証環境反映済み', order: 4, color: '#ffeb3b' },
  { name: 'production_deployed', display_name: '本番環境反映済み', order: 5, color: '#51cf66' },
  { name: 'cancelled', display_name: '中止', order: 6, color: '#dc3545' },
] as const
