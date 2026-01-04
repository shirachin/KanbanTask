/**
 * AG Grid関連の定数
 */

/**
 * ページサイズの選択肢
 */
export const PAGE_SIZE_OPTIONS = [25, 50, 100, 200] as const

/**
 * デフォルトのページサイズ
 */
export const DEFAULT_PAGE_SIZE = 50

/**
 * 状態復元のリトライ回数の上限
 */
export const MAX_RETRY_COUNT = 50

/**
 * 状態復元のタイムアウト値（ミリ秒）
 */
export const RESTORE_STATE_TIMEOUTS = {
  INITIAL: 100,
  COMPLETE: 200,
  GRID_READY: 300,
  FIRST_DATA_RENDERED: 500,
} as const
