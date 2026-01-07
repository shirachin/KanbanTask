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
          <div class="task-list">
            <div 
              v-for="task in getTasksByStatus(status.id)" 
              :key="task.id" 
              class="task-card"
              @click="openTaskEditModal(task)"
            >
              <div class="task-title">{{ task.title }}</div>
              <div v-if="task.description" class="task-description">{{ task.description }}</div>
              
              <!-- TODOリスト -->
              <div class="task-todos">
                <div 
                  v-for="todo in getTodosForTask(task.id)" 
                  :key="todo.id" 
                  class="todo-item"
                >
                  <input
                    type="checkbox"
                    :checked="todo.completed"
                    disabled
                    class="todo-checkbox"
                    title="完了状態は実行完了日で自動管理されます"
                  />
                  <span 
                    class="todo-title"
                    :class="{ 'todo-completed': todo.completed }"
                  >
                    {{ todo.title }}
                  </span>
                  <button
                    type="button"
                    class="todo-delete-button"
                    @click.stop.prevent="deleteTodoItem(todo.id)"
                    title="削除"
                  >
                    <span class="material-symbols-outlined">delete</span>
                  </button>
                </div>
                <div class="todo-add-container">
                  <input
                    v-model="newTodoTexts[task.id]"
                    @keyup.enter="addTodo(task.id)"
                    @blur="handleTodoBlur(task.id)"
                    @click.stop
                    type="text"
                    class="todo-add-input"
                    placeholder="+ TODOを追加"
                  />
                </div>
              </div>
              
              <div class="task-project">{{ getProjectName(task.project_id) }}</div>
            </div>
            <p v-if="getTasksByStatus(status.id).length === 0" class="empty-message">タスクがありません</p>
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
    
    <TaskEditModal
      v-model:show="showTaskEditModal"
      :task="editingTask"
      :projects="myProjects"
      :current-user="currentUser"
      @save="handleTaskUpdate"
      @delete="handleTaskDelete"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useProjects, type Project } from '../composables/useProjects'
import { useTasks, type Task } from '../composables/useTasks'
import { useTodos, type Todo } from '../composables/useTodos'
import { useStatuses, type Status } from '../composables/useStatuses'
import TaskCreateModal from '../components/TaskCreateModal.vue'
import TaskEditModal from '../components/TaskEditModal.vue'
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
const { tasks, loading: tasksLoading, error: tasksError, fetchTasks, createTask, updateTask } = useTasks()
const { fetchTodos, createTodo, deleteTodo, getTodos } = useTodos()
const { statuses: statusesData, fetchStatuses: fetchStatusesData } = useStatuses()

const showTaskModal = ref(false)
const showTaskEditModal = ref(false)
const editingTask = ref<Task | null>(null)
const newTodoTexts = ref<Record<number, string>>({})

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

// プロジェクト名を取得
const getProjectName = (projectId: number): string => {
  if (projectId === -1) {
    return '個人タスク'
  }
  const project = projects.value.find((p: Project) => p.id === projectId)
  return project ? project.name : '不明'
}

// タスクのTODOリストを取得
const getTodosForTask = (taskId: number): Todo[] => {
  return getTodos(taskId)
}

// TODOを追加
const addTodo = async (taskId: number) => {
  const text = newTodoTexts.value[taskId]?.trim()
  if (!text) {
    return
  }
  
  try {
    await createTodo(taskId, text)
    newTodoTexts.value[taskId] = ''
  } catch (e) {
    console.error('Error adding todo:', e)
  }
}

// TODO入力フィールドのblur処理
const handleTodoBlur = (taskId: number) => {
  // blur時は空の場合は何もしない（Enterキーでの追加のみ）
  const text = newTodoTexts.value[taskId]?.trim()
  if (!text) {
    delete newTodoTexts.value[taskId]
  }
}


// TODOを削除
const deleteTodoItem = async (todoId: number) => {
  if (!confirm('このTODOを削除しますか？')) {
    return
  }
  
  try {
    await deleteTodo(todoId)
  } catch (e) {
    console.error('Error deleting todo:', e)
  }
}

// タスク編集モーダルを開く
const openTaskEditModal = (task: Task) => {
  editingTask.value = task
  showTaskEditModal.value = true
}

// タスク更新処理
const handleTaskUpdate = async (taskData: {
  id: number
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
    
    await updateTask(taskData.id, {
      title: taskData.title,
      description: taskData.description,
      status: taskData.status,
      status_id: statusId,
      assignee: taskData.assignee,
    })
    
    // タスクを再読み込み
    await loadTasks()
  } catch (e) {
    console.error('Error updating task:', e)
    alert('タスクの更新に失敗しました')
  }
}

// タスク削除処理
const handleTaskDelete = async (taskId: number) => {
  try {
    // タスクを再読み込み（削除はTaskEditModal内で実行済み）
    await loadTasks()
  } catch (e) {
    console.error('Error reloading tasks after deletion:', e)
  }
}

// ステータスIDでタスクを取得（個人タスクの場合はstatus名でマッチング）
const getTasksByStatus = (statusId: number): Task[] => {
  // 個人タスク用の仮想ステータスID（負の値）の場合は、status名でマッチング
  if (statusId < 0) {
    const statusNameMap: { [key: number]: string } = {
      [-1]: 'considering',
      [-2]: 'not_started',
      [-3]: 'in_progress',
      [-4]: 'review_pending',
      [-5]: 'staging_deployed',
      [-6]: 'production_deployed',
      [-7]: 'cancelled'
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
    
    // 各タスクのTODOを取得
    for (const task of tasks.value) {
      try {
        await fetchTodos(task.id)
      } catch (e) {
        console.error(`Error fetching todos for task ${task.id}:`, e)
      }
    }
    
    // ステータスを取得（共通ステータスを取得）
    await fetchStatuses()
    
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
})

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

.task-todos {
  margin: 0.75rem 0;
  padding-top: 0.75rem;
  border-top: 1px solid var(--current-borderColor);
}

.todo-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  padding: 0.25rem 0;
  
  &:last-child {
    margin-bottom: 0;
  }
}

.todo-checkbox {
  cursor: pointer;
  width: 1rem;
  height: 1rem;
  flex-shrink: 0;
}

.todo-title {
  flex: 1;
  font-size: 0.875rem;
  color: var(--current-textPrimary);
  word-break: break-word;
  
  &.todo-completed {
    text-decoration: line-through;
    color: var(--current-textSecondary);
    opacity: 0.7;
  }
}

.todo-delete-button {
  background: none;
  border: none;
  color: var(--current-textSecondary);
  cursor: pointer;
  padding: 0.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: background-color 0.2s, color 0.2s;
  flex-shrink: 0;
  opacity: 0;
  
  .task-card:hover & {
    opacity: 1;
  }
  
  &:hover {
    background: var(--current-backgroundGray);
    color: var(--current-errorColor);
  }
  
  .material-symbols-outlined {
    font-size: 1rem;
  }
}

.task-card {
  cursor: pointer;
  
  // TODO関連の要素はクリックイベントを伝播させない
  .task-todos,
  .todo-item,
  .todo-add-container {
    pointer-events: auto;
  }
  
  .todo-delete-button {
    pointer-events: auto;
  }
}

.todo-add-container {
  margin-top: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px solid var(--current-borderColor);
}

.todo-add-input {
  width: 100%;
  padding: 0.375rem 0.5rem;
  border: 1px solid var(--current-borderColor);
  border-radius: 4px;
  background: var(--current-backgroundLight);
  color: var(--current-textPrimary);
  font-size: 0.875rem;
  transition: border-color 0.2s;
  
  &:focus {
    outline: none;
    border-color: var(--current-linkColor);
  }
  
  &::placeholder {
    color: var(--current-textSecondary);
  }
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
