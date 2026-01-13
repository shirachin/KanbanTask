import { ref } from 'vue'
import { apiGet, apiPost, apiPut, apiDelete, handleApiError } from '../utils/apiClient'

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

export const useTasks = () => {
  const tasks = ref<Task[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // タスク一覧を取得
  const fetchTasks = async (projectId?: number, projectIds?: number[], assignee?: string) => {
    loading.value = true
    error.value = null
    try {
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
      
      const queryString = params.toString()
      const endpoint = `/api/v1/tasks${queryString ? `?${queryString}` : ''}`
      
      const data = await apiGet<Task[]>(endpoint)
      tasks.value = data
    } catch (e) {
      error.value = handleApiError(e, 'タスクの取得に失敗しました')
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
      const data = await apiPost<Task>('/api/v1/tasks', task)
      tasks.value.push(data)
      return data
    } catch (e) {
      error.value = handleApiError(e, 'タスクの作成に失敗しました')
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
      const data = await apiPut<Task>(`/api/v1/tasks/${id}`, task)
      const index = tasks.value.findIndex((t: Task) => t.id === id)
      if (index !== -1) {
        tasks.value[index] = data
      }
      return data
    } catch (e) {
      error.value = handleApiError(e, 'タスクの更新に失敗しました')
      console.error('Error updating task:', e)
      throw e
    } finally {
      loading.value = false
    }
  }

  // タスクの順番を更新
  const updateTaskOrder = async (id: number, newOrder: number) => {
    loading.value = true
    error.value = null
    try {
      const data = await apiPut<Task>(`/api/v1/tasks/${id}/order?new_order=${newOrder}`, {})
      const index = tasks.value.findIndex((t: Task) => t.id === id)
      if (index !== -1) {
        tasks.value[index] = data
      }
      return data
    } catch (e) {
      error.value = handleApiError(e, 'タスクの順番更新に失敗しました')
      console.error('Error updating task order:', e)
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
      await apiDelete(`/api/v1/tasks/${id}`)
      tasks.value = tasks.value.filter((t: Task) => t.id !== id)
    } catch (e) {
      error.value = handleApiError(e, 'タスクの削除に失敗しました')
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
    updateTaskOrder,
    deleteTask,
  }
}
