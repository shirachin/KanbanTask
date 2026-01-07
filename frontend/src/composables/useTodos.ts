import { ref } from 'vue'
import { apiGet, apiPost, apiPut, apiDelete, handleApiError } from '../utils/apiClient'

export type Todo = {
  id: number
  task_id: number
  title: string
  completed: boolean
  order: number
  scheduled_date?: string | null  // 実行予定日 (YYYY-MM-DD形式)
  completed_date?: string | null  // 実行完了日 (YYYY-MM-DD形式)
  created_at?: string
  updated_at?: string | null
}

export type TodoListResponse = {
  items: Array<{
    id: number
    task_id: number
    title: string
    completed: boolean
    order: number
    scheduled_date?: string | null
    completed_date?: string | null
    created_at?: string | null
    updated_at?: string | null
    task_name?: string | null
    project_id?: number | null
    project_name?: string | null
  }>
  total: number
  skip: number
  limit: number
}

export const useTodos = () => {
  const todos = ref<Map<number, Todo[]>>(new Map()) // task_id -> todos[]
  const loading = ref(false)
  const error = ref<string | null>(null)

  // タスクのTODO一覧を取得
  const fetchTodos = async (taskId: number) => {
    loading.value = true
    error.value = null
    try {
      const data = await apiGet<Todo[]>(`/api/v1/tasks/${taskId}/todos`)
      todos.value.set(taskId, data)
      return data
    } catch (e) {
      // エラーが発生した場合も空の配列を返す（エンドポイントが存在しない場合など）
      error.value = handleApiError(e, 'TODOの取得に失敗しました')
      console.error('Error fetching todos:', e)
      todos.value.set(taskId, [])
      return []
    } finally {
      loading.value = false
    }
  }

  // TODOを作成
  const createTodo = async (taskId: number, title: string) => {
    loading.value = true
    error.value = null
    try {
      const data = await apiPost<Todo>(`/api/v1/tasks/${taskId}/todos`, {
        task_id: taskId,
        title: title,
        completed: false,
        order: 0,
      })
      const taskTodos = todos.value.get(taskId) || []
      taskTodos.push(data)
      todos.value.set(taskId, taskTodos)
      return data
    } catch (e) {
      error.value = handleApiError(e, 'TODOの作成に失敗しました')
      console.error('Error creating todo:', e)
      throw e
    } finally {
      loading.value = false
    }
  }

  // TODOを更新
  const updateTodo = async (todoId: number, todo: Partial<Omit<Todo, 'id' | 'task_id' | 'created_at' | 'updated_at'>>) => {
    loading.value = true
    error.value = null
    try {
      const data = await apiPut<Todo>(`/api/v1/todos/${todoId}`, todo)
      
      // 該当するタスクのTODOリストを更新
      for (const [taskId, taskTodos] of todos.value.entries()) {
        const index = taskTodos.findIndex((t: Todo) => t.id === todoId)
        if (index !== -1) {
          taskTodos[index] = data
          todos.value.set(taskId, [...taskTodos])
          break
        }
      }
      
      return data
    } catch (e) {
      error.value = handleApiError(e, 'TODOの更新に失敗しました')
      console.error('Error updating todo:', e)
      throw e
    } finally {
      loading.value = false
    }
  }

  // TODOを削除
  const deleteTodo = async (todoId: number) => {
    loading.value = true
    error.value = null
    try {
      await apiDelete(`/api/v1/todos/${todoId}`)
      
      // 該当するタスクのTODOリストから削除
      for (const [taskId, taskTodos] of todos.value.entries()) {
        const filtered = taskTodos.filter((t: Todo) => t.id !== todoId)
        if (filtered.length !== taskTodos.length) {
          todos.value.set(taskId, filtered)
          break
        }
      }
    } catch (e) {
      error.value = handleApiError(e, 'TODOの削除に失敗しました')
      console.error('Error deleting todo:', e)
      throw e
    } finally {
      loading.value = false
    }
  }

  // タスクのTODOリストを取得（キャッシュから）
  const getTodos = (taskId: number): Todo[] => {
    return todos.value.get(taskId) || []
  }

  // すべてのTODOを取得（ページネーション対応）
  const fetchAllTodos = async (skip: number = 0, limit: number = 100) => {
    loading.value = true
    error.value = null
    try {
      const data = await apiGet<TodoListResponse>(`/api/v1/todos?skip=${skip}&limit=${limit}`)
      return data
    } catch (e) {
      error.value = handleApiError(e, 'TODOの取得に失敗しました')
      console.error('Error fetching all todos:', e)
      throw e
    } finally {
      loading.value = false
    }
  }

  return {
    todos,
    loading,
    error,
    fetchTodos,
    fetchAllTodos,
    createTodo,
    updateTodo,
    deleteTodo,
    getTodos,
  }
}
