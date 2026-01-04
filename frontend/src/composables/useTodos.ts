import { ref } from 'vue'

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

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const useTodos = () => {
  const todos = ref<Map<number, Todo[]>>(new Map()) // task_id -> todos[]
  const loading = ref(false)
  const error = ref<string | null>(null)

  // タスクのTODO一覧を取得
  const fetchTodos = async (taskId: number) => {
    loading.value = true
    error.value = null
    try {
      const response = await fetch(`${API_URL}/api/v1/tasks/${taskId}/todos`)
      if (!response.ok) {
        // 404の場合は空の配列を返す（TODOがまだ存在しない場合）
        if (response.status === 404) {
          todos.value.set(taskId, [])
          return []
        }
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const data = await response.json()
      todos.value.set(taskId, data)
      return data
    } catch (e) {
      // エラーが発生した場合も空の配列を返す（エンドポイントが存在しない場合など）
      error.value = e instanceof Error ? e.message : 'TODOの取得に失敗しました'
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
      const response = await fetch(`${API_URL}/api/v1/tasks/${taskId}/todos`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          task_id: taskId,
          title: title,
          completed: false,
          order: 0,
        }),
      })
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const data = await response.json()
      const taskTodos = todos.value.get(taskId) || []
      taskTodos.push(data)
      todos.value.set(taskId, taskTodos)
      return data
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'TODOの作成に失敗しました'
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
      const response = await fetch(`${API_URL}/api/v1/todos/${todoId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(todo),
      })
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const data = await response.json()
      
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
      error.value = e instanceof Error ? e.message : 'TODOの更新に失敗しました'
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
      const response = await fetch(`${API_URL}/api/v1/todos/${todoId}`, {
        method: 'DELETE',
      })
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      // 該当するタスクのTODOリストから削除
      for (const [taskId, taskTodos] of todos.value.entries()) {
        const filtered = taskTodos.filter((t: Todo) => t.id !== todoId)
        if (filtered.length !== taskTodos.length) {
          todos.value.set(taskId, filtered)
          break
        }
      }
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'TODOの削除に失敗しました'
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
      const response = await fetch(`${API_URL}/api/v1/todos?skip=${skip}&limit=${limit}`)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const data = await response.json()
      return data
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'TODOの取得に失敗しました'
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
