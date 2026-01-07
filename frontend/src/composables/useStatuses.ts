import { ref } from 'vue'
import { apiGet, handleApiError } from '../utils/apiClient'

export type Status = {
  id: number
  name: string
  display_name: string
  order: number
  color: string
  project_id: number | null
  created_at?: string
}

export const useStatuses = () => {
  const statuses = ref<Status[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // ステータス一覧を取得
  const fetchStatuses = async (projectId?: number) => {
    loading.value = true
    error.value = null
    try {
      const endpoint = projectId 
        ? `/api/v1/statuses?project_id=${projectId}`
        : '/api/v1/statuses'
      const data = await apiGet<Status[]>(endpoint)
      statuses.value = data
      return data
    } catch (e) {
      error.value = handleApiError(e, 'ステータスの取得に失敗しました')
      console.error('Error fetching statuses:', e)
      return []
    } finally {
      loading.value = false
    }
  }

  return {
    statuses,
    loading,
    error,
    fetchStatuses,
  }
}
