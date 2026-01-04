import { ref } from 'vue'

export type Project = {
  id: number
  name: string
  startMonth: string
  endMonth: string
  assignee: string[]
  description?: string | null
  created_at?: string
  updated_at?: string | null
}

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const useProjects = () => {
  const projects = ref<Project[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // プロジェクト一覧を取得
  const fetchProjects = async (assignee?: string) => {
    loading.value = true
    error.value = null
    try {
      let url = `${API_URL}/api/v1/projects`
      if (assignee) {
        url += `?assignee=${encodeURIComponent(assignee)}`
      }
      const response = await fetch(url)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const data = await response.json()
      // バックエンドの形式（start_month, end_month）からフロントエンドの形式（startMonth, endMonth）に変換
      projects.value = data.map((p: any) => ({
        id: p.id,
        name: p.name,
        startMonth: p.start_month || '',
        endMonth: p.end_month || '',
        assignee: Array.isArray(p.assignee) ? p.assignee : [],
        description: p.description,
        created_at: p.created_at,
        updated_at: p.updated_at,
      }))
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'プロジェクトの取得に失敗しました'
      console.error('Error fetching projects:', e)
    } finally {
      loading.value = false
    }
  }

  // プロジェクトを作成
  const createProject = async (project: Omit<Project, 'id' | 'created_at' | 'updated_at'>) => {
    loading.value = true
    error.value = null
    try {
      const response = await fetch(`${API_URL}/api/v1/projects`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: project.name,
          start_month: project.startMonth || null,
          end_month: project.endMonth || null,
          assignee: project.assignee || [],
          description: project.description || null,
        }),
      })
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const data = await response.json()
      // バックエンドの形式からフロントエンドの形式に変換
      const newProject: Project = {
        id: data.id,
        name: data.name,
        startMonth: data.start_month || '',
        endMonth: data.end_month || '',
        assignee: Array.isArray(data.assignee) ? data.assignee : [],
        description: data.description,
        created_at: data.created_at,
        updated_at: data.updated_at,
      }
      projects.value.push(newProject)
      return newProject
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'プロジェクトの作成に失敗しました'
      console.error('Error creating project:', e)
      throw e
    } finally {
      loading.value = false
    }
  }

  // プロジェクトを更新
  const updateProject = async (id: number, project: Partial<Omit<Project, 'id' | 'created_at' | 'updated_at'>>) => {
    loading.value = true
    error.value = null
    try {
      const response = await fetch(`${API_URL}/api/v1/projects/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: project.name,
          start_month: project.startMonth !== undefined ? project.startMonth : null,
          end_month: project.endMonth !== undefined ? project.endMonth : null,
          assignee: project.assignee || [],
          description: project.description || null,
        }),
      })
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const data = await response.json()
      // バックエンドの形式からフロントエンドの形式に変換
      const updatedProject: Project = {
        id: data.id,
        name: data.name,
        startMonth: data.start_month || '',
        endMonth: data.end_month || '',
        assignee: Array.isArray(data.assignee) ? data.assignee : [],
        description: data.description,
        created_at: data.created_at,
        updated_at: data.updated_at,
      }
      const index = projects.value.findIndex((p: Project) => p.id === id)
      if (index !== -1) {
        projects.value[index] = updatedProject
      }
      return updatedProject
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'プロジェクトの更新に失敗しました'
      console.error('Error updating project:', e)
      throw e
    } finally {
      loading.value = false
    }
  }

  // プロジェクトを削除
  const deleteProject = async (id: number) => {
    loading.value = true
    error.value = null
    try {
      const response = await fetch(`${API_URL}/api/v1/projects/${id}`, {
        method: 'DELETE',
      })
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      projects.value = projects.value.filter((p: Project) => p.id !== id)
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'プロジェクトの削除に失敗しました'
      console.error('Error deleting project:', e)
      throw e
    } finally {
      loading.value = false
    }
  }

  return {
    projects,
    loading,
    error,
    fetchProjects,
    createProject,
    updateProject,
    deleteProject,
  }
}
