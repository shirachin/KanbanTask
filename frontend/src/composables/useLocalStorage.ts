/**
 * LocalStorage管理用のユーティリティ関数
 */

// LocalStorageから値を取得
export const getLocalStorage = <T>(key: string, defaultValue: T): T => {
  try {
    const item = localStorage.getItem(key)
    if (item === null) {
      return defaultValue
    }
    const parsed = JSON.parse(item) as T
    return parsed
  } catch (e) {
    console.error(`Error reading from localStorage key "${key}":`, e)
    return defaultValue
  }
}

// LocalStorageに値を保存
export const setLocalStorage = <T>(key: string, value: T): void => {
  try {
    if (value === null || value === undefined) {
      localStorage.removeItem(key)
    } else {
      const serialized = JSON.stringify(value)
      localStorage.setItem(key, serialized)
    }
  } catch (e) {
    console.error(`Error writing to localStorage key "${key}":`, e)
  }
}

// LocalStorageから値を削除
export const removeLocalStorage = (key: string): void => {
  try {
    localStorage.removeItem(key)
  } catch (e) {
    console.error(`Error removing from localStorage key "${key}":`, e)
  }
}

// LocalStorageのキー定数
export const STORAGE_KEYS = {
  // TODOリスト
  TODO_LIST_PAGE_SIZE: 'todoList_pageSize',
  TODO_LIST_COLUMN_STATE: 'todoList_columnState',
  TODO_LIST_FILTER_MODEL: 'todoList_filterModel',
  TODO_LIST_SORT_MODEL: 'todoList_sortModel',
  
  // プロジェクト管理
  PROJECT_MANAGEMENT_PAGE_SIZE: 'projectManagement_pageSize',
  PROJECT_MANAGEMENT_COLUMN_STATE: 'projectManagement_columnState',
  PROJECT_MANAGEMENT_FILTER_MODEL: 'projectManagement_filterModel',
  
  // カンバンボード
  KANBAN_PROJECT_MODE: 'kanban_projectMode',
  KANBAN_PROJECT_ID: 'kanban_projectId',
  
  // アプリ全体
  APP_CURRENT_USER: 'app_currentUser',
  APP_CURRENT_VIEW: 'app_currentView',
} as const
