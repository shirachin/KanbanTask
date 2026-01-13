<template>
  <div class="kanban-board">
    <div class="kanban-header">
      <h2>カンバンボード</h2>
      <div class="header-actions">
        <div class="project-selector">
          <select v-model="selectedProjectMode" @change="handleProjectModeChange" class="project-select">
            <option value="all">自身が担当するすべてのプロジェクト+個人的タスク</option>
            <option value="search">プロジェクト検索（自分の担当プロジェクト）</option>
            <option value="personal">個人的タスク</option>
          </select>
          <!-- プロジェクト検索コンボボックス（Vuetify Autocomplete風） -->
          <div v-if="selectedProjectMode === 'search'" class="project-search-container">
            <div class="project-search-input-wrapper">
              <input
                v-model="projectSearchQuery"
                @focus="handleProjectSearchFocus"
                @blur="handleProjectSearchBlur"
                @input="handleProjectSearchInput"
                @keydown.enter.prevent="handleProjectSearchEnter"
                @keydown.arrow-down.prevent="navigateProjectDropdown(1)"
                @keydown.arrow-up.prevent="navigateProjectDropdown(-1)"
                @keydown.escape="showProjectDropdown = false"
                type="text"
                class="project-search-input"
                :placeholder="selectedProjectName || 'プロジェクトを検索...'"
                autocomplete="off"
              />
              <span 
                v-if="selectedProjectId" 
                class="project-search-clear" 
                @click.stop="clearProjectSelection"
                title="クリア"
              >
                <span class="material-symbols-outlined">close</span>
              </span>
              <span 
                v-else
                class="project-search-arrow" 
                @click.stop="showProjectDropdown = !showProjectDropdown"
              >
                <span class="material-symbols-outlined">{{ showProjectDropdown ? 'expand_less' : 'expand_more' }}</span>
              </span>
            </div>
            <div v-if="showProjectDropdown && (projectSearchQuery || filteredProjects.length > 0)" class="project-search-dropdown">
              <div
                v-if="filteredProjects.length === 0 && projectSearchQuery.trim()"
                class="project-search-no-results"
              >
                プロジェクトが見つかりません
              </div>
              <div
                v-for="(project, index) in filteredProjects"
                :key="project.id"
                :class="['project-search-option', { 'project-search-option-selected': index === selectedProjectIndex, 'project-search-option-active': selectedProjectId === project.id }]"
                @mousedown.prevent="selectProject(project.id, project.name)"
                @mouseenter="selectedProjectIndex = index"
              >
                {{ project.name }}
              </div>
            </div>
          </div>
          <select 
            v-if="selectedProjectMode === 'search' && selectedProjectId" 
            v-model="selectedAssignee" 
            @change="handleAssigneeChange"
            class="project-select"
          >
            <option value="">すべての担当者</option>
            <option v-for="assignee in availableAssignees" :key="assignee" :value="assignee">
              {{ assignee }}
            </option>
          </select>
        </div>
        <button type="button" class="add-task-button" @click="showTaskModal = true" :disabled="loading">
          <span class="material-symbols-outlined">add</span>
          タスク追加
        </button>
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
          <VueDraggable
            v-if="tasksByStatusMap[status.id] !== undefined"
            v-model="tasksByStatusMap[status.id]"
            :group="{ name: 'kanban-tasks', pull: true, put: true }"
            :animation="150"
            ghost-class="sortable-ghost"
            chosen-class="sortable-chosen"
            drag-class="sortable-drag"
            item-key="id"
            class="task-list"
            :data-status-id="status.id"
            @end="(evt) => handleDragEnd(evt, status.id)"
          >
            <template #item="{ element }">
              <div class="task-card" :data-task-id="element.id">
                <div class="task-title">{{ element.title }}</div>
              </div>
            </template>
            <template #footer>
              <p v-if="tasksByStatusMap[status.id] && tasksByStatusMap[status.id].length === 0" class="empty-message">タスクがありません</p>
            </template>
          </VueDraggable>
          <div v-else class="task-list" :data-status-id="status.id">
            <p class="empty-message">読み込み中...</p>
          </div>
        </div>
      </div>
    </div>
    
    <TaskCreateModal
      v-model:show="showTaskModal"
      :projects="myProjects"
      :current-user="currentUser"
      @save="handleTaskSave"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { VueDraggable } from 'vue-draggable-plus'
import { useProjects, type Project } from '../composables/useProjects'
import { useTasks, type Task } from '../composables/useTasks'
import { useTodos, type Todo } from '../composables/useTodos'
import { useStatuses, type Status } from '../composables/useStatuses'
import TaskCreateModal from '../components/TaskCreateModal.vue'
import { DEFAULT_PERSONAL_STATUSES } from '../constants/statuses'
import { apiGet } from '../utils/apiClient'

type ProjectMode = 'all' | 'search' | 'personal'

// LocalStorage管理
import { getLocalStorage, setLocalStorage, STORAGE_KEYS } from '../composables/useLocalStorage'

const currentUser = ref<string | null>(getLocalStorage<string | null>(STORAGE_KEYS.APP_CURRENT_USER, null))

// LocalStorageから選択状態を復元
const initialMode = getLocalStorage<ProjectMode>(STORAGE_KEYS.KANBAN_PROJECT_MODE, 'all')
// プロジェクト検索モードの場合は、プロジェクトIDをnull（デフォルト）にする
const initialProjectId = initialMode === 'search' ? null : getLocalStorage<number | null>(STORAGE_KEYS.KANBAN_PROJECT_ID, null)

const selectedProjectMode = ref<ProjectMode>(initialMode)
const selectedProjectId = ref<number | null>(initialProjectId)
const selectedAssignee = ref<string>('') // プロジェクト検索モード用の担当者選択（'' = すべての担当者）

// プロジェクト検索用の状態
const projectSearchQuery = ref<string>('')
const showProjectDropdown = ref<boolean>(false)
const selectedProjectIndex = ref<number>(-1)
const selectedProjectName = ref<string>('')

const { projects, loading: projectsLoading, error: projectsError, fetchProjects } = useProjects()
const { tasks, loading: tasksLoading, error: tasksError, fetchTasks, createTask, updateTask, updateTaskOrder } = useTasks()
const { fetchTodos, createTodo, deleteTodo, getTodos } = useTodos()
const { statuses: statusesData, fetchStatuses: fetchStatusesData } = useStatuses()

const showTaskModal = ref(false)

// 各ステータスのタスクリストを管理（Draggable用）
const tasksByStatusMap = ref<Record<number, Task[]>>({})


const loading = computed(() => projectsLoading.value || tasksLoading.value)
const error = computed(() => projectsError.value || tasksError.value)

// 現在のユーザーが担当するプロジェクト
const myProjects = computed(() => {
  if (!currentUser.value) return []
  return projects.value.filter((p: Project) => 
    p.assignee && p.assignee.includes(currentUser.value!)
  )
})

// プロジェクト検索用のフィルタリング
const filteredProjects = computed(() => {
  if (!projectSearchQuery.value.trim()) {
    return myProjects.value
  }
  const query = projectSearchQuery.value.toLowerCase().trim()
  return myProjects.value.filter((p: Project) =>
    p.name.toLowerCase().includes(query)
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

// ステータス一覧（共通ステータスを使用）
const statuses = computed(() => {
  if (statusesData.value && statusesData.value.length > 0) {
    return statusesData.value.sort((a: Status, b: Status) => (a.order || 0) - (b.order || 0))
  }
  // フォールバック: デフォルトステータスを使用
  return DEFAULT_PERSONAL_STATUSES.map(status => ({
    id: 0,
    name: status.name,
    display_name: status.display_name,
    order: status.order,
    color: status.color,
    project_id: null,
  }))
})

// プロジェクト検索モード用の利用可能な担当者一覧
const availableAssignees = ref<string[]>([])

// プロジェクトのタスクから担当者一覧を取得（プロジェクトの担当者も含む）
const fetchAssigneesForProject = async (projectId: number) => {
  try {
    const assignees = new Set<string>()
    
    // プロジェクトの担当者を追加
    const project = projects.value.find((p: Project) => p.id === projectId)
    if (project && project.assignee) {
      project.assignee.forEach((a: string) => assignees.add(a))
    }
    
    // プロジェクトのタスクから担当者を追加
    try {
      const projectTasks = await apiGet<Task[]>(`/api/v1/tasks?project_id=${projectId}`)
      projectTasks.forEach((task: Task) => {
        if (task.assignee) {
          assignees.add(task.assignee)
        }
      })
    } catch (e) {
      console.error('Error fetching tasks for assignees:', e)
    }
    
    availableAssignees.value = Array.from(assignees).sort()
  } catch (e) {
    console.error('Error fetching assignees:', e)
    availableAssignees.value = []
  }
}



// ステータスIDでタスクを取得（orderでソート）
const getTasksByStatus = (statusId: number): Task[] => {
  // ステータスオブジェクトを取得
  const status = statuses.value.find((s: Status) => s.id === statusId)
  if (!status) {
    return []
  }
  
  const filteredTasks = tasks.value.filter((task: Task) => {
    // status_idが一致する場合
    if (task.status_id === statusId) {
      return true
    }
    // status_idがnullまたは0の場合、status名でマッチング（フォールバック）
    if ((task.status_id === null || task.status_id === 0) && task.status === status.name) {
      return true
    }
    // 日本語のstatus名とのマッピング（後方互換性のため）
    const statusNameMap: { [key: string]: string } = {
      '未着手': 'not_started',
      '検討中': 'considering',
      '実行中': 'in_progress',
      'レビュー待ち': 'review_pending',
      '検証環境反映済み': 'staging_deployed',
      '本番環境反映済み': 'production_deployed',
      '中止': 'cancelled'
    }
    const mappedStatusName = statusNameMap[task.status] || task.status
    if (mappedStatusName === status.name) {
      return true
    }
    return false
  })
  
  // orderでソート
  return filteredTasks.sort((a: Task, b: Task) => {
    return (a.order || 0) - (b.order || 0)
  })
}

// ステータスごとのタスクリストを更新
const updateTasksByStatus = () => {
  console.log('updateTasksByStatus called', {
    statusesCount: statuses.value.length,
    tasksCount: tasks.value.length,
    statuses: statuses.value.map(s => ({ id: s.id, name: s.name })),
    tasks: tasks.value.map(t => ({ id: t.id, status_id: t.status_id, status: t.status }))
  })
  if (statuses.value.length === 0) {
    console.warn('updateTasksByStatus: statuses is empty')
    return
  }
  statuses.value.forEach((status: Status) => {
    const tasks = getTasksByStatus(status.id)
    tasksByStatusMap.value[status.id] = tasks || []
    console.log(`Status ${status.id} (${status.name}): ${tasks.length} tasks`, tasks.map(t => t.id))
  })
  console.log('tasksByStatusMap after update:', tasksByStatusMap.value)
}

// 個人タスク用のプロジェクト取得は不要（project_id=-1で扱う）

// ステータスを取得（共通ステータスを取得）
const fetchStatuses = async () => {
  await fetchStatusesData()
}

// プロジェクトモード変更時の処理
const handleProjectModeChange = async () => {
  selectedProjectId.value = null
  selectedProjectName.value = ''
  projectSearchQuery.value = ''
  selectedAssignee.value = '' // 担当者選択をリセット
  availableAssignees.value = []
  showProjectDropdown.value = false
  selectedProjectIndex.value = -1
  // LocalStorageに保存
  setLocalStorage(STORAGE_KEYS.KANBAN_PROJECT_MODE, selectedProjectMode.value)
  setLocalStorage(STORAGE_KEYS.KANBAN_PROJECT_ID, null)
  await loadTasks()
}

// プロジェクト選択処理
const selectProject = async (projectId: number, projectName: string) => {
  selectedProjectId.value = projectId
  selectedProjectName.value = projectName
  projectSearchQuery.value = projectName
  showProjectDropdown.value = false
  selectedProjectIndex.value = -1
  
  // LocalStorageに保存
  setLocalStorage(STORAGE_KEYS.KANBAN_PROJECT_MODE, selectedProjectMode.value)
  setLocalStorage(STORAGE_KEYS.KANBAN_PROJECT_ID, selectedProjectId.value)
  
  // プロジェクトが選択された場合、そのプロジェクトのタスクから担当者一覧を取得
  selectedAssignee.value = '' // 担当者選択をリセット
  await fetchAssigneesForProject(selectedProjectId.value)
  
  await loadTasks()
}

// プロジェクト検索フォーカス処理
const handleProjectSearchFocus = () => {
  showProjectDropdown.value = true
  // 選択されているプロジェクト名を検索クエリに設定
  if (selectedProjectName.value && !projectSearchQuery.value) {
    projectSearchQuery.value = selectedProjectName.value
  }
}

// プロジェクト検索入力処理
const handleProjectSearchInput = () => {
  showProjectDropdown.value = true
  selectedProjectIndex.value = -1
  // 検索クエリが変更されたら、選択をクリア
  if (projectSearchQuery.value !== selectedProjectName.value) {
    selectedProjectId.value = null
    selectedProjectName.value = ''
    selectedAssignee.value = ''
    availableAssignees.value = []
  }
}

// プロジェクト選択をクリア
const clearProjectSelection = () => {
  selectedProjectId.value = null
  selectedProjectName.value = ''
  projectSearchQuery.value = ''
  selectedAssignee.value = ''
  availableAssignees.value = []
  showProjectDropdown.value = false
  selectedProjectIndex.value = -1
  setLocalStorage(STORAGE_KEYS.KANBAN_PROJECT_ID, null)
  loadTasks()
}

// プロジェクト検索のblur処理（少し遅延させてクリックイベントを処理）
const handleProjectSearchBlur = () => {
  setTimeout(() => {
    showProjectDropdown.value = false
  }, 200)
}

// プロジェクト検索のEnterキー処理
const handleProjectSearchEnter = () => {
  if (selectedProjectIndex.value >= 0 && selectedProjectIndex.value < filteredProjects.value.length) {
    const project = filteredProjects.value[selectedProjectIndex.value]
    selectProject(project.id, project.name)
  } else if (filteredProjects.value.length === 1) {
    const project = filteredProjects.value[0]
    selectProject(project.id, project.name)
  }
}

// プロジェクト検索のドロップダウンナビゲーション
const navigateProjectDropdown = (direction: number) => {
  if (!showProjectDropdown.value) {
    showProjectDropdown.value = true
    return
  }
  
  const maxIndex = filteredProjects.value.length - 1
  selectedProjectIndex.value += direction
  
  if (selectedProjectIndex.value < 0) {
    selectedProjectIndex.value = maxIndex
  } else if (selectedProjectIndex.value > maxIndex) {
    selectedProjectIndex.value = 0
  }
}

// 担当者変更時の処理
const handleAssigneeChange = async () => {
  await loadTasks()
}

// タスクを読み込む
const loadTasks = async () => {
  try {
    if (displayProjectIds.value.length === 0) {
      tasks.value = []
      statuses.value = []
      return
    }
    
    let assignee: string | undefined = undefined
    
    if (selectedProjectMode.value === 'all') {
      // 「自分が担当するすべてのプロジェクト+個人的タスク」モードの場合
      // 各プロジェクトのタスクで、自分が担当者になっているタスクのみを表示
      assignee = currentUser.value || undefined
    } else if (selectedProjectMode.value === 'search') {
      // 「プロジェクト検索」モードの場合
      // 選択された担当者でフィルタリング（「すべての担当者」の場合はundefined）
      assignee = selectedAssignee.value && selectedAssignee.value !== '' ? selectedAssignee.value : undefined
    } else if (selectedProjectMode.value === 'personal') {
      // 「個人的タスク」モードの場合
      assignee = currentUser.value || undefined
    }
    
    if (displayProjectIds.value.length === 1) {
      await fetchTasks(displayProjectIds.value[0], undefined, assignee)
    } else {
      await fetchTasks(undefined, displayProjectIds.value, assignee)
    }
    
    // ステータスを取得（共通ステータスを取得）
    await fetchStatuses()
    
    // タスク読み込み後、ステータスごとのタスクリストを更新
    // ステータスが読み込まれた後に更新する
    if (statuses.value.length > 0) {
      updateTasksByStatus()
    }
    
  } catch (e) {
    console.error('Error in loadTasks:', e)
  }
}

// 初期化
onMounted(async () => {
  if (!currentUser.value) return
  
  // プロジェクト一覧を取得
  await fetchProjects(currentUser.value)
  
  // プロジェクト検索モードでプロジェクトが既に選択されている場合、担当者一覧を取得
  if (selectedProjectMode.value === 'search' && selectedProjectId.value) {
    const project = myProjects.value.find((p: Project) => p.id === selectedProjectId.value)
    if (project) {
      selectedProjectName.value = project.name
      projectSearchQuery.value = project.name
    }
    await fetchAssigneesForProject(selectedProjectId.value)
  }
  
  // タスクを読み込む（個人タスクはproject_id=-1で扱う）
  await loadTasks()
  
  // ステータスごとのタスクリストを更新
  // ステータスが読み込まれた後に更新する
  if (statuses.value.length > 0) {
    updateTasksByStatus()
  }
})

// ドラッグ終了時の処理
const handleDragEnd = (evt: { from: HTMLElement, to: HTMLElement, oldIndex: number, newIndex: number }, toStatusId: number) => {
  if (evt.oldIndex === undefined || evt.newIndex === undefined) return
  
  // 移動元のステータスIDを取得
  const fromStatusId = evt.from ? parseInt(evt.from.getAttribute('data-status-id') || '0') : 0
  
  // 移動したタスクを特定（移動元のリストから取得）
  let movedTask: Task | null = null
  if (fromStatusId && tasksByStatusMap.value[fromStatusId]) {
    const fromTasks = tasksByStatusMap.value[fromStatusId]
    if (evt.oldIndex >= 0 && evt.oldIndex < fromTasks.length) {
      movedTask = fromTasks[evt.oldIndex]
    }
  }
  
  // 移動先のリストから取得（v-modelで既に更新されているため）
  if (!movedTask && tasksByStatusMap.value[toStatusId]) {
    const toTasks = tasksByStatusMap.value[toStatusId]
    if (evt.newIndex >= 0 && evt.newIndex < toTasks.length) {
      movedTask = toTasks[evt.newIndex]
    }
  }
  
  if (!movedTask) return
  
  const taskId = movedTask.id
  
  // ステータスオブジェクトを取得
  const newStatus = statuses.value.find((s: Status) => s.id === toStatusId)
  if (!newStatus) return
  
  // 同一ステータス内での移動の場合は、orderを更新
  if (fromStatusId === toStatusId) {
    // 同一ステータス内での順番変更
    const newOrder = evt.newIndex
    handleTaskOrderChange(taskId, toStatusId, newOrder)
  } else {
    // ステータスが変更された場合
    handleTaskStatusChange(taskId, newStatus.name, toStatusId)
  }
}

// タスクのステータス変更処理
const handleTaskStatusChange = async (taskId: number, newStatusName: string, newStatusId: number) => {
  try {
    await updateTask(taskId, {
      status: newStatusName,
      status_id: newStatusId,
    })
    
    // タスクを再読み込み
    await loadTasks()
    
    // ステータスごとのタスクリストを更新
    updateTasksByStatus()
  } catch (e) {
    console.error('Error updating task status:', e)
    alert('タスクのステータス更新に失敗しました')
    // エラー時はタスクを再読み込みして元に戻す
    await loadTasks()
    updateTasksByStatus()
  }
}

// タスクの順番変更処理
const handleTaskOrderChange = async (taskId: number, statusId: number, newOrder: number) => {
  try {
    // バックエンドAPIで順番を更新（同じステータス内のすべてのタスクのorderを適切に調整）
    await updateTaskOrder(taskId, newOrder)
    
    // タスクを再読み込み
    await loadTasks()
    
    // ステータスごとのタスクリストを更新
    updateTasksByStatus()
  } catch (e) {
    console.error('Error updating task order:', e)
    alert('タスクの順番更新に失敗しました')
    // エラー時はタスクを再読み込みして元に戻す
    await loadTasks()
    updateTasksByStatus()
  }
}


// タスク保存処理
const handleTaskSave = async (taskData: {
  project_id: number
  title: string
  description?: string | null
  status: string
  assignee?: string | null
}) => {
  try {
    // ステータスIDを取得（共通ステータスから取得）
    let statusId: number | null = null
    const statusesList = statusesData.value || []
    const status = statusesList.find((s: Status) => s.name === taskData.status)
    if (status) {
      statusId = status.id
    }
    
    await createTask({
      project_id: taskData.project_id,
      title: taskData.title,
      description: taskData.description,
      status: taskData.status,
      status_id: statusId,
      order: 0,
      completed: false,
      assignee: taskData.assignee,
    })
    
    // タスクを再読み込み
    await loadTasks()
    
    // 新しく作成されたタスクのTODOを取得
    const newTask = tasks.value[tasks.value.length - 1]
    if (newTask) {
      await fetchTodos(newTask.id)
    }
  } catch (e) {
    console.error('Error creating task:', e)
    alert('タスクの作成に失敗しました')
  }
}

// プロジェクトモードまたはプロジェクトIDが変更されたらタスクを再読み込み
watch([selectedProjectMode, selectedProjectId, displayProjectIds], () => {
  // LocalStorageに保存（watch内で更新することで、プログラム的な変更も反映）
  setLocalStorage(STORAGE_KEYS.KANBAN_PROJECT_MODE, selectedProjectMode.value)
  setLocalStorage(STORAGE_KEYS.KANBAN_PROJECT_ID, selectedProjectId.value)
  loadTasks().then(() => {
    updateTasksByStatus()
  })
})

// タスクが変更されたら、ステータスごとのタスクリストを更新
watch(tasks, () => {
  updateTasksByStatus()
}, { deep: true })
</script>

<style lang="scss" scoped>
@import '../styles/_theme';

.kanban-board {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 1rem;
  box-sizing: border-box;
}

.kanban-header {
  margin-bottom: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  flex-shrink: 0;

  h2 {
    margin: 0;
    color: var(--current-textPrimary);
    font-size: 2rem;
    font-weight: 600;
  }
}

.header-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

.project-selector {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.add-task-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1rem;
  border: 1px solid var(--current-borderColor);
  border-radius: 4px;
  background: var(--current-activeBackground);
  color: var(--current-textWhite);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s, border-color 0.2s;

  &:hover:not(:disabled) {
    background: var(--current-linkColor);
    border-color: var(--current-linkColor);
  }

  &:active:not(:disabled) {
    transform: scale(0.98);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .material-symbols-outlined {
    font-size: 1.25rem;
  }
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

// プロジェクト検索コンボボックス
.project-search-container {
  position: relative;
  min-width: 250px;
}

.project-search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.project-search-input {
  width: 100%;
  padding: 0.5rem 2.5rem 0.5rem 1rem;
  border: 1px solid var(--current-borderColor);
  border-radius: 4px;
  background: var(--current-backgroundLight);
  color: var(--current-textPrimary);
  font-size: 0.875rem;
  
  &:focus {
    outline: none;
    border-color: var(--current-linkColor);
  }
  
  &::placeholder {
    color: var(--current-textSecondary);
  }
}

.project-search-arrow,
.project-search-clear {
  position: absolute;
  right: 0.5rem;
  top: 50%;
  transform: translateY(-50%);
  cursor: pointer;
  color: var(--current-textSecondary);
  display: flex;
  align-items: center;
  padding: 0.25rem;
  
  &:hover {
    color: var(--current-textPrimary);
  }
  
  .material-symbols-outlined {
    font-size: 1.25rem;
  }
}

.project-search-clear {
  &:hover {
    color: var(--current-errorColor);
  }
}

.project-search-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 0.25rem;
  background: var(--current-backgroundLight);
  border: 1px solid var(--current-borderColor);
  border-radius: 4px;
  box-shadow: 0 4px 12px var(--current-shadowMd);
  max-height: 300px;
  overflow-y: auto;
  z-index: 1000;
}

.project-search-option {
  padding: 0.75rem 1rem;
  cursor: pointer;
  color: var(--current-textPrimary);
  transition: background-color 0.2s;
  
  &:hover,
  &.project-search-option-selected {
    background: var(--current-backgroundGray);
  }
  
  &.project-search-option-active {
    background: var(--current-primaryColor);
    color: var(--current-textWhite);
    font-weight: 600;
  }
}

.project-search-no-results {
  padding: 0.75rem 1rem;
  color: var(--current-textSecondary);
  text-align: center;
  font-style: italic;
}

.loading-message {
  text-align: center;
  padding: 2rem;
  color: var(--current-textSecondary);
  font-size: 1rem;
}

.error-message {
  background: var(--current-errorBackground);
  color: var(--current-errorText);
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1rem;
  border: 1px solid var(--current-errorBorder);
}

.kanban-content {
  flex: 1;
  overflow-x: auto;
  overflow-y: auto;
  min-height: 0;
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
  display: flex;
  flex-direction: column;
  min-height: fit-content;
  box-sizing: border-box;
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
  flex: 1;
  min-height: 200px;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  overflow-y: auto;
  overflow-x: hidden;
}

.task-card {
  background: var(--current-backgroundGray);
  border-radius: 6px;
  padding: 1rem;
  cursor: grab;
  transition: transform 0.2s, box-shadow 0.2s;
  border: 1px solid var(--current-borderColor);
  user-select: none;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px var(--current-shadowMd);
  }
  
  &:active {
    cursor: grabbing;
  }
}

.task-title {
  font-weight: 600;
  color: var(--current-textPrimary);
  font-size: 0.9375rem;
  word-break: break-word;
}

.sortable-ghost {
  opacity: 0.4;
}

.sortable-chosen {
  cursor: grabbing;
}

.sortable-drag {
  opacity: 0.8;
}

.empty-message {
  margin: 0;
  color: var(--current-textSecondary);
  font-size: 0.875rem;
  text-align: center;
  padding: 2rem 0;
}
</style>
