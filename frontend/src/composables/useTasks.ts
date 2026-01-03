import { ref } from 'vue'

export type Task = {
  id: number
  title: string
  description?: string | null
  status: string
  status_id?: number | null
  order: number
  completed: boolean
  project_id: number
  assignee?: string | null  // 担当者（個人タスク用、project_id=-1の場合に使用）
  created_at?: string
  updated_at?: string | null
}

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const useTasks = () => {
  const tasks = ref<Task[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // タスク一覧を取得
  const fetchTasks = async (projectId?: number, projectIds?: number[], assignee?: string) => {
    loading.value = true
    error.value = null
    try {
      let url = `${API_URL}/api/tasks`
      const params = new URLSearchParams()
      
      if (projectId !== undefined) {
        params.append('project_id', projectId.toString())
      } else if (projectIds && projectIds.length > 0) {
        params.append('project_ids', projectIds.join(','))
      }
      
      // assigneeが指定されている場合は追加（個人タスク用）
      if (assignee) {
        params.append('assignee', assignee)
      }
      
      if (params.toString()) {
        url += `?${params.toString()}`
      }
      
      const response = await fetch(url)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const data = await response.json()
      tasks.value = data
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'タスクの取得に失敗しました'
      console.error('Error fetching tasks:', e)
    } finally {
      loading.value = false
    }
  }

  // タスクを作成
  const createTask = async (task: Omit<Task, 'id' | 'created_at' | 'updated_at'>) => {
    loading.value = true
    error.value = null
    try {
      const response = await fetch(`${API_URL}/api/tasks`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(task),
      })
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const data = await response.json()
      tasks.value.push(data)
      return data
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'タスクの作成に失敗しました'
      console.error('Error creating task:', e)
      throw e
    } finally {
      loading.value = false
    }
  }

  // タスクを更新
  const updateTask = async (id: number, task: Partial<Omit<Task, 'id' | 'created_at' | 'updated_at'>>) => {
    loading.value = true
    error.value = null
    try {
      const response = await fetch(`${API_URL}/api/tasks/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(task),
      })
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const data = await response.json()
      const index = tasks.value.findIndex((t: Task) => t.id === id)
      if (index !== -1) {
        tasks.value[index] = data
      }
      return data
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'タスクの更新に失敗しました'
      console.error('Error updating task:', e)
      throw e
    } finally {
      loading.value = false
    }
  }

  // タスクを削除
  const deleteTask = async (id: number) => {
    loading.value = true
    error.value = null
    try {
      const response = await fetch(`${API_URL}/api/tasks/${id}`, {
        method: 'DELETE',
      })
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      tasks.value = tasks.value.filter((t: Task) => t.id !== id)
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'タスクの削除に失敗しました'
      console.error('Error deleting task:', e)
      throw e
    } finally {
      loading.value = false
    }
  }

  return {
    tasks,
    loading,
    error,
    fetchTasks,
    createTask,
    updateTask,
    deleteTask,
  }
}
