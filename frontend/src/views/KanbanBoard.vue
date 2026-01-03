<template>
  <div class="kanban-board">
    <div class="kanban-header">
      <h2>カンバンボード</h2>
      <div class="project-selector">
        <select v-model="selectedProjectMode" @change="handleProjectModeChange" class="project-select">
          <option value="all">自身が担当するすべてのプロジェクト+個人的タスク</option>
          <option value="search">プロジェクト検索（自分の担当プロジェクト）</option>
          <option value="personal">個人的タスク</option>
        </select>
        <select 
          v-if="selectedProjectMode === 'search'" 
          v-model="selectedProjectId" 
          @change="handleProjectChange"
          class="project-select"
        >
          <option value="">プロジェクトを選択</option>
          <option v-for="project in myProjects" :key="project.id" :value="project.id">
            {{ project.name }}
          </option>
        </select>
      </div>
    </div>
    
    <div v-if="loading" class="loading-message">データを読み込み中...</div>
    <div v-else-if="error" class="error-message">{{ error }}</div>
    <div v-else class="kanban-content">
      <div class="kanban-columns">
        <div 
          v-for="status in statuses" 
          :key="status.id" 
          class="kanban-column"
        >
          <h3 class="column-title" :style="{ borderBottomColor: status.color }">
            {{ status.display_name }}
          </h3>
          <div class="task-list">
            <div 
              v-for="task in getTasksByStatus(status.id)" 
              :key="task.id" 
              class="task-card"
            >
              <div class="task-title">{{ task.title }}</div>
              <div v-if="task.description" class="task-description">{{ task.description }}</div>
              <div class="task-project">{{ getProjectName(task.project_id) }}</div>
            </div>
            <p v-if="getTasksByStatus(status.id).length === 0" class="empty-message">タスクがありません</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useProjects, type Project } from '../composables/useProjects'
import { useTasks, type Task } from '../composables/useTasks'

type ProjectMode = 'all' | 'search' | 'personal'

// URLパラメータからユーザー名を取得
const getUrlUser = (): string | null => {
  const params = new URLSearchParams(window.location.search)
  return params.get('user')
}

const currentUser = ref<string | null>(getUrlUser())
const selectedProjectMode = ref<ProjectMode>('all')
const selectedProjectId = ref<number | null>(null)

const { projects, loading: projectsLoading, error: projectsError, fetchProjects } = useProjects()
const { tasks, loading: tasksLoading, error: tasksError, fetchTasks } = useTasks()

const loading = computed(() => projectsLoading.value || tasksLoading.value)
const error = computed(() => projectsError.value || tasksError.value)

// 現在のユーザーが担当するプロジェクト
const myProjects = computed(() => {
  if (!currentUser.value) return []
  return projects.value.filter((p: Project) => 
    p.assignee && p.assignee.includes(currentUser.value!)
  )
})

// 表示するプロジェクトIDのリスト（個人タスクは-1で扱う）
const displayProjectIds = computed(() => {
  if (selectedProjectMode.value === 'personal') {
    // 個人タスクの場合はproject_id=-1
    return [-1]
  } else if (selectedProjectMode.value === 'search') {
    return selectedProjectId.value ? [selectedProjectId.value] : []
  } else {
    // すべてのプロジェクト + 個人的タスク（-1）
    const projectIds = myProjects.value.map((p: Project) => p.id)
    projectIds.push(-1)  // 個人タスクを追加
    return projectIds
  }
})

// ステータス一覧（最初のプロジェクトのステータスを使用、またはデフォルトステータス）
const statuses = ref<Array<{ id: number; name: string; display_name: string; order: number; color: string; project_id: number }>>([])

// プロジェクト名を取得
const getProjectName = (projectId: number): string => {
  if (projectId === -1) {
    return '個人タスク'
  }
  const project = projects.value.find((p: Project) => p.id === projectId)
  return project ? project.name : '不明'
}

// ステータスIDでタスクを取得（個人タスクの場合はstatus名でマッチング）
const getTasksByStatus = (statusId: number): Task[] => {
  // 個人タスク用の仮想ステータスID（負の値）の場合は、status名でマッチング
  if (statusId < 0) {
    const statusNameMap: { [key: number]: string } = {
      [-1]: 'todo',
      [-2]: 'doing',
      [-3]: 'review',
      [-4]: 'done'
    }
    const statusName = statusNameMap[statusId]
    if (statusName) {
      return tasks.value.filter((task: Task) => {
        return task.project_id === -1 && task.status === statusName
      })
    }
  }
  return tasks.value.filter((task: Task) => {
    return task.status_id === statusId
  })
}

// 個人タスク用のプロジェクト取得は不要（project_id=-1で扱う）

// ステータスを取得
const fetchStatuses = async (projectId: number) => {
  try {
    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
    const response = await fetch(`${API_URL}/api/statuses?project_id=${projectId}`)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    const data = await response.json()
    if (data.length > 0) {
      statuses.value = data.sort((a: any, b: any) => a.order - b.order)
    } else {
      // デフォルトステータスを使用（project_id=-1の場合など）
      statuses.value = [
        { id: -1, name: 'todo', display_name: '未着手', order: 0, color: '#667eea', project_id: projectId },
        { id: -2, name: 'doing', display_name: '進行中', order: 1, color: '#ffa726', project_id: projectId },
        { id: -3, name: 'review', display_name: 'レビュー中', order: 2, color: '#9c27b0', project_id: projectId },
        { id: -4, name: 'done', display_name: '完了', order: 3, color: '#51cf66', project_id: projectId }
      ]
    }
  } catch (e) {
    console.error('Error fetching statuses:', e)
    // デフォルトステータスを使用
    statuses.value = [
      { id: -1, name: 'todo', display_name: '未着手', order: 0, color: '#667eea', project_id: projectId },
      { id: -2, name: 'doing', display_name: '進行中', order: 1, color: '#ffa726', project_id: projectId },
      { id: -3, name: 'review', display_name: 'レビュー中', order: 2, color: '#9c27b0', project_id: projectId },
      { id: -4, name: 'done', display_name: '完了', order: 3, color: '#51cf66', project_id: projectId }
    ]
  }
}

// プロジェクトモード変更時の処理
const handleProjectModeChange = async () => {
  selectedProjectId.value = null
  await loadTasks()
}

// プロジェクト変更時の処理
const handleProjectChange = async () => {
  await loadTasks()
}

// タスクを読み込む
const loadTasks = async () => {
  if (displayProjectIds.value.length === 0) {
    tasks.value = []
    return
  }
  
  // 個人タスク（-1）が含まれている場合は、assigneeパラメータを追加
  const hasPersonalTasks = displayProjectIds.value.includes(-1)
  const assignee = hasPersonalTasks && currentUser.value ? currentUser.value : undefined
  
  if (displayProjectIds.value.length === 1) {
    await fetchTasks(displayProjectIds.value[0], undefined, assignee)
  } else {
    await fetchTasks(undefined, displayProjectIds.value, assignee)
  }
  
  // ステータスを取得
  // 個人タスクのみの場合は-1、それ以外の場合は最初のプロジェクトIDを使用
  const statusProjectId = displayProjectIds.value.includes(-1) && displayProjectIds.value.length === 1 
    ? -1 
    : displayProjectIds.value.find(id => id !== -1) ?? displayProjectIds.value[0]
  if (statusProjectId !== undefined) {
    await fetchStatuses(statusProjectId)
  }
}

// 初期化
onMounted(async () => {
  if (!currentUser.value) return
  
  // プロジェクト一覧を取得
  await fetchProjects(currentUser.value)
  
  // タスクを読み込む（個人タスクはproject_id=-1で扱う）
  await loadTasks()
})

// プロジェクトモードまたはプロジェクトIDが変更されたらタスクを再読み込み
watch([selectedProjectMode, selectedProjectId, displayProjectIds], () => {
  loadTasks()
})
</script>

<style lang="scss" scoped>
@import '../styles/_theme';

.kanban-board {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.kanban-header {
  margin-bottom: 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;

  h2 {
    margin: 0;
    color: var(--current-textPrimary);
    font-size: 2rem;
    font-weight: 600;
  }
}

.project-selector {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.project-select {
  padding: 0.625rem 1rem;
  border: 1px solid var(--current-borderColor);
  border-radius: 4px;
  background: var(--current-backgroundLight);
  color: var(--current-textPrimary);
  font-size: 0.875rem;
  cursor: pointer;
  transition: border-color 0.2s;

  &:focus {
    outline: none;
    border-color: var(--current-linkColor);
  }
}

.loading-message {
  text-align: center;
  padding: 2rem;
  color: var(--current-textSecondary);
  font-size: 1rem;
}

.error-message {
  background: #f8d7da;
  color: #721c24;
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1rem;
  border: 1px solid #f5c6cb;
}

.kanban-content {
  overflow-x: auto;
}

.kanban-columns {
  display: flex;
  gap: 1.5rem;
  min-width: fit-content;
}

.kanban-column {
  flex: 1;
  min-width: 280px;
  background: var(--current-backgroundLight);
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px var(--current-shadowMd);
}

.column-title {
  margin: 0 0 1rem 0;
  color: var(--current-textPrimary);
  font-size: 1.125rem;
  font-weight: 600;
  padding-bottom: 0.75rem;
  border-bottom: 3px solid;
}

.task-list {
  min-height: 200px;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.task-card {
  background: var(--current-backgroundGray);
  border-radius: 6px;
  padding: 1rem;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  border: 1px solid var(--current-borderColor);

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px var(--current-shadowMd);
  }
}

.task-title {
  font-weight: 600;
  color: var(--current-textPrimary);
  margin-bottom: 0.5rem;
  font-size: 0.9375rem;
}

.task-description {
  color: var(--current-textSecondary);
  font-size: 0.875rem;
  margin-bottom: 0.5rem;
  line-height: 1.4;
}

.task-project {
  color: var(--current-textSecondary);
  font-size: 0.75rem;
  margin-top: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px solid var(--current-borderColor);
}

.empty-message {
  margin: 0;
  color: var(--current-textSecondary);
  font-size: 0.875rem;
  text-align: center;
  padding: 2rem 0;
}
</style>
