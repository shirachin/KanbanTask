<template>
  <div v-if="show" class="modal-overlay" @click.self="handleCancel">
    <div class="modal-content">
      <div class="modal-header">
        <h3>タスク編集</h3>
        <button type="button" class="modal-close" @click="handleCancel">
          <span class="material-symbols-outlined">close</span>
        </button>
      </div>
      
      <div class="modal-body">
        <div class="form-group">
          <label for="edit-task-project">
            対象プロジェクト
            <span class="required-mark">*</span>
          </label>
          <select
            id="edit-task-project"
            v-model="formData.project_id"
            class="form-input"
            :class="{ 'form-input-error': errors.project_id }"
            @change="handleProjectChange"
            required
            :disabled="true"
          >
            <option value="">プロジェクトを選択</option>
            <option v-for="project in availableProjects" :key="project.id" :value="project.id">
              {{ project.name }}
            </option>
          </select>
          <span v-if="errors.project_id" class="error-message">{{ errors.project_id }}</span>
        </div>
        
        <div class="form-group">
          <label for="edit-task-title">
            タスク名
            <span class="required-mark">*</span>
          </label>
          <input
            id="edit-task-title"
            v-model="formData.title"
            type="text"
            class="form-input"
            :class="{ 'form-input-error': errors.title }"
            placeholder="タスク名を入力"
            required
          />
          <span v-if="errors.title" class="error-message">{{ errors.title }}</span>
        </div>
        
        <div class="form-group">
          <label for="edit-task-description">詳細</label>
          <textarea
            id="edit-task-description"
            v-model="formData.description"
            class="form-input form-textarea"
            placeholder="タスクの詳細を入力"
            rows="4"
          />
        </div>
        
        <div class="form-group">
          <label for="edit-task-status">
            フェーズ
            <span class="required-mark">*</span>
          </label>
          <select
            id="edit-task-status"
            v-model="formData.status"
            class="form-input"
            :class="{ 'form-input-error': errors.status }"
            :disabled="loadingStatuses"
            required
          >
            <option value="">フェーズを選択</option>
            <option v-for="status in availableStatuses" :key="status.id" :value="status.name">
              {{ status.display_name }}
            </option>
          </select>
          <span v-if="errors.status" class="error-message">{{ errors.status }}</span>
          <span v-if="loadingStatuses" class="loading-hint">ステータスを読み込み中...</span>
        </div>
        
        <div class="form-group">
          <label for="edit-task-assignee">担当者</label>
          <select
            id="edit-task-assignee"
            v-model="formData.assignee"
            class="form-input"
          >
            <option value="">担当者を選択（任意）</option>
            <option v-for="assignee in availableAssignees" :key="assignee" :value="assignee">
              {{ assignee }}
            </option>
          </select>
        </div>
        
        <div class="form-group">
          <label>TODO</label>
          <div class="todo-list-container">
            <div 
              v-for="todo in taskTodos" 
              :key="todo.id" 
              class="todo-item"
            >
              <div class="todo-main-row">
                <input
                  type="checkbox"
                  :checked="todo.completed"
                  disabled
                  class="todo-checkbox"
                  title="完了状態は実行完了日で自動管理されます"
                />
                <input
                  v-if="editingTodoId === todo.id"
                  v-model="editingTodoTitle"
                  @blur="saveTodoEdit(todo.id)"
                  @keyup.enter="saveTodoEdit(todo.id)"
                  @keyup.esc="cancelTodoEdit"
                  type="text"
                  class="todo-edit-input"
                  @click.stop
                />
                <span 
                  v-else
                  class="todo-title"
                  :class="{ 'todo-completed': todo.completed }"
                  @dblclick="startTodoEdit(todo.id, todo.title)"
                >
                  {{ todo.title }}
                </span>
                <button
                  type="button"
                  class="todo-delete-button"
                  @click.stop="deleteTodoItem(todo.id)"
                  title="削除"
                >
                  <span class="material-symbols-outlined">delete</span>
                </button>
              </div>
              <div class="todo-dates-row">
                <div class="todo-date-field">
                  <label class="todo-date-label">実行予定日</label>
                  <input
                    type="date"
                    :value="todo.scheduled_date ? formatDateForInput(todo.scheduled_date) : ''"
                    @change="updateTodoDate(todo.id, 'scheduled_date', ($event.target as HTMLInputElement).value)"
                    class="todo-date-input"
                    @click.stop
                  />
                </div>
                <div class="todo-date-field">
                  <label class="todo-date-label">実行完了日</label>
                  <input
                    type="date"
                    :value="todo.completed_date ? formatDateForInput(todo.completed_date) : ''"
                    @change="updateTodoDate(todo.id, 'completed_date', ($event.target as HTMLInputElement).value)"
                    class="todo-date-input"
                    @click.stop
                  />
                </div>
              </div>
            </div>
            <div class="todo-add-container">
              <input
                v-model="newTodoText"
                @keyup.enter="addTodo"
                @blur="handleTodoBlur"
                type="text"
                class="todo-add-input"
                placeholder="+ TODOを追加"
              />
            </div>
          </div>
        </div>
      </div>
      
      <div class="modal-footer">
        <button type="button" class="button button-cancel" @click="handleCancel">
          キャンセル
        </button>
        <button type="button" class="button button-save" @click="handleSave" :disabled="loadingStatuses">
          保存
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed, reactive, onMounted } from 'vue'
import type { Project } from '../composables/useProjects'
import type { Task } from '../composables/useTasks'
import { useTodos, type Todo } from '../composables/useTodos'

type Status = {
  id: number
  name: string
  display_name: string
  order: number
  color: string
  project_id: number
}

const props = defineProps<{
  show: boolean
  task: Task | null
  projects: Project[]
  currentUser: string | null
}>()

const emit = defineEmits<{
  'update:show': [value: boolean]
  'save': [task: {
    id: number
    project_id: number
    title: string
    description?: string | null
    status: string
    assignee?: string | null
  }]
}>()

const formData = ref({
  id: 0,
  project_id: '',
  title: '',
  description: '',
  status: '',
  assignee: '',
})

const errors = reactive({
  project_id: '',
  title: '',
  status: '',
})

const loadingStatuses = ref(false)
const availableStatuses = ref<Status[]>([])

// TODO管理
const { fetchTodos, createTodo, updateTodo, deleteTodo, getTodos } = useTodos()
const taskTodos = ref<Todo[]>([])
const newTodoText = ref('')
const editingTodoId = ref<number | null>(null)
const editingTodoTitle = ref('')

// 利用可能なプロジェクト（個人タスクを含む）
const availableProjects = computed(() => {
  const projects = [...props.projects]
  // 個人タスクを追加
  projects.push({
    id: -1,
    name: '個人タスク',
    startMonth: '',
    endMonth: '',
    assignee: props.currentUser ? [props.currentUser] : [],
    description: null,
    created_at: undefined,
    updated_at: null,
  })
  return projects
})

// 利用可能な担当者（選択されたプロジェクトの担当者 + 現在のユーザー）
const availableAssignees = computed(() => {
  const assignees = new Set<string>()
  
  if (props.currentUser) {
    assignees.add(props.currentUser)
  }
  
  if (formData.value.project_id) {
    const projectId = parseInt(formData.value.project_id.toString())
    if (projectId === -1) {
      // 個人タスクの場合は現在のユーザーのみ
      if (props.currentUser) {
        assignees.add(props.currentUser)
      }
    } else {
      const project = props.projects.find((p: Project) => p.id === projectId)
      if (project && project.assignee) {
        project.assignee.forEach((a: string) => assignees.add(a))
      }
    }
  }
  
  return Array.from(assignees).sort()
})

// プロジェクト変更時にステータスを取得
const handleProjectChange = async () => {
  if (!formData.value.project_id) {
    availableStatuses.value = []
    return
  }
  
  const projectId = parseInt(formData.value.project_id.toString())
  loadingStatuses.value = true
  
  try {
    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
    const response = await fetch(`${API_URL}/api/v1/statuses?project_id=${projectId}`)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    const data = await response.json()
    if (data.length > 0) {
      availableStatuses.value = data.sort((a: Status, b: Status) => a.order - b.order)
    } else {
      // デフォルトステータスを使用
      availableStatuses.value = DEFAULT_PERSONAL_STATUSES.map(status => ({
        ...status,
        project_id: projectId,
      }))
    }
  } catch (e) {
    console.error('Error fetching statuses:', e)
    // デフォルトステータスを使用
    availableStatuses.value = DEFAULT_PERSONAL_STATUSES.map(status => ({
      ...status,
      project_id: projectId,
    }))
  } finally {
    loadingStatuses.value = false
  }
}

// モーダルが開かれたときにフォームを初期化
watch([() => props.show, () => props.task], async ([newShow, newTask]) => {
  if (newShow && newTask) {
    // エラーをリセット
    errors.project_id = ''
    errors.title = ''
    errors.status = ''
    
    // フォームにタスクデータを設定
    formData.value = {
      id: newTask.id,
      project_id: newTask.project_id.toString(),
      title: newTask.title,
      description: newTask.description || '',
      status: newTask.status,
      assignee: newTask.assignee || '',
    }
    
    // ステータスを取得
    await handleProjectChange()
    
    // TODOを取得
    await loadTodos(newTask.id)
  } else {
    // モーダルが閉じられたときにリセット
    taskTodos.value = []
    newTodoText.value = ''
    editingTodoId.value = null
    editingTodoTitle.value = ''
  }
}, { immediate: true })

// TODOを読み込む
const loadTodos = async (taskId: number) => {
  await fetchTodos(taskId)
  taskTodos.value = getTodos(taskId)
}

// TODOを追加
const addTodo = async () => {
  if (!props.task) return
  
  const text = newTodoText.value.trim()
  if (!text) {
    return
  }
  
  try {
    await createTodo(props.task.id, text)
    newTodoText.value = ''
    taskTodos.value = getTodos(props.task.id)
  } catch (e) {
    console.error('Error adding todo:', e)
  }
}

// TODO入力フィールドのblur処理
const handleTodoBlur = () => {
  const text = newTodoText.value.trim()
  if (!text) {
    newTodoText.value = ''
  }
}

// TODO編集を開始
const startTodoEdit = (todoId: number, title: string) => {
  editingTodoId.value = todoId
  editingTodoTitle.value = title
}

// TODO編集を保存
const saveTodoEdit = async (todoId: number) => {
  if (!props.task) return
  
  const text = editingTodoTitle.value.trim()
  if (!text) {
    // 空の場合は削除
    await deleteTodoItem(todoId)
    return
  }
  
  try {
    await updateTodo(todoId, { title: text })
    editingTodoId.value = null
    editingTodoTitle.value = ''
    taskTodos.value = getTodos(props.task.id)
  } catch (e) {
    console.error('Error updating todo:', e)
  }
}

// TODO編集をキャンセル
const cancelTodoEdit = () => {
  editingTodoId.value = null
  editingTodoTitle.value = ''
}

// 日付をinput[type="date"]用の形式（YYYY-MM-DD）に変換
const formatDateForInput = (dateString: string): string => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

// TODOの日付を更新
const updateTodoDate = async (todoId: number, field: 'scheduled_date' | 'completed_date', value: string) => {
  if (!props.task) return
  
  try {
    const updateData: { scheduled_date?: string | null; completed_date?: string | null; completed?: boolean } = {}
    updateData[field] = value || null
    
    // 実行完了日が設定された場合は自動的にcompletedをtrueに、削除された場合はfalseに
    if (field === 'completed_date') {
      updateData.completed = value ? true : false
    }
    
    await updateTodo(todoId, updateData)
    taskTodos.value = getTodos(props.task.id)
  } catch (e) {
    console.error('Error updating todo date:', e)
  }
}

// TODOを削除
const deleteTodoItem = async (todoId: number) => {
  if (!confirm('このTODOを削除しますか？')) {
    return
  }
  
  try {
    await deleteTodo(todoId)
    if (props.task) {
      taskTodos.value = getTodos(props.task.id)
    }
  } catch (e) {
    console.error('Error deleting todo:', e)
  }
}

const handleCancel = () => {
  emit('update:show', false)
}

const validateForm = (): boolean => {
  // エラーをリセット
  errors.project_id = ''
  errors.title = ''
  errors.status = ''
  
  let isValid = true
  
  // プロジェクトのバリデーション
  if (!formData.value.project_id) {
    errors.project_id = '対象プロジェクトは必須です。'
    isValid = false
  }
  
  // タスク名のバリデーション
  if (!formData.value.title.trim()) {
    errors.title = 'タスク名は必須です。'
    isValid = false
  }
  
  // ステータスのバリデーション
  if (!formData.value.status) {
    errors.status = 'フェーズは必須です。'
    isValid = false
  }
  
  return isValid
}

const handleSave = () => {
  if (!validateForm()) {
    return
  }
  
  const projectId = parseInt(formData.value.project_id.toString())
  
  emit('save', {
    id: formData.value.id,
    project_id: projectId,
    title: formData.value.title.trim(),
    description: formData.value.description.trim() || null,
    status: formData.value.status,
    assignee: formData.value.assignee || (projectId === -1 ? props.currentUser : null),
  })
  emit('update:show', false)
}
</script>

<style lang="scss" scoped>
@import '../styles/_theme';

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--current-modalOverlay);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: var(--current-backgroundLight);
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 20px var(--current-shadowMd);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid var(--current-borderColor);

  h3 {
    margin: 0;
    color: var(--current-textPrimary);
    font-size: 1.25rem;
    font-weight: 600;
  }
}

.modal-close {
  background: none;
  border: none;
  color: var(--current-textSecondary);
  cursor: pointer;
  padding: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: background-color 0.2s;

  &:hover {
    background: var(--current-backgroundGray);
  }

  .material-symbols-outlined {
    font-size: 1.5rem;
  }
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  flex: 1;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1.5rem;
  border-top: 1px solid var(--current-borderColor);
}

.form-group {
  margin-bottom: 1.5rem;

  &:last-child {
    margin-bottom: 0;
  }
}

label {
  display: block;
  margin-bottom: 0.5rem;
  color: var(--current-textPrimary);
  font-size: 0.875rem;
  font-weight: 500;
}

.required-mark {
  color: var(--current-errorColor);
  margin-left: 0.25rem;
}

.form-input {
  width: 100%;
  padding: 0.625rem 1rem;
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

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  &.form-input-error {
    border-color: var(--current-errorColor);
  }
}

.form-textarea {
  resize: vertical;
  min-height: 100px;
  font-family: inherit;
}

.error-message {
  display: block;
  color: var(--current-errorColor);
  font-size: 0.75rem;
  margin-top: 0.25rem;
}

.loading-hint {
  display: block;
  color: var(--current-textSecondary);
  font-size: 0.75rem;
  margin-top: 0.25rem;
}

.button {
  padding: 0.625rem 1.5rem;
  border: none;
  border-radius: 4px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s, transform 0.1s;

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  &:active:not(:disabled) {
    transform: scale(0.98);
  }
}

.button-cancel {
  background: var(--current-backgroundGray);
  color: var(--current-textPrimary);

  &:hover:not(:disabled) {
    background: var(--current-buttonHoverBackground);
  }
}

.button-save {
  background: var(--current-activeBackground);
  color: var(--current-textWhite);

  &:hover:not(:disabled) {
    background: var(--current-linkColor);
  }
}

.todo-list-container {
  border: 1px solid var(--current-borderColor);
  border-radius: 4px;
  padding: 0.75rem;
  background: var(--current-backgroundGray);
  max-height: 300px;
  overflow-y: auto;
}

.todo-item {
  margin-bottom: 0.75rem;
  padding: 0.5rem;
  border: 1px solid var(--current-borderColor);
  border-radius: 4px;
  background: var(--current-backgroundLight);
  
  &:last-child {
    margin-bottom: 0;
  }
}

.todo-main-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.todo-dates-row {
  display: flex;
  gap: 1rem;
  padding-left: 1.5rem;
  flex-wrap: wrap;
}

.todo-date-field {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  flex: 1;
  min-width: 150px;
}

.todo-date-label {
  font-size: 0.75rem;
  color: var(--current-textSecondary);
  font-weight: 500;
}

.todo-date-input {
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
  cursor: text;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  transition: background-color 0.2s;
  
  &:hover {
    background: var(--current-backgroundLight);
  }
  
  &.todo-completed {
    text-decoration: line-through;
    color: var(--current-textSecondary);
    opacity: 0.7;
  }
}

.todo-edit-input {
  flex: 1;
  padding: 0.25rem 0.5rem;
  border: 1px solid var(--current-linkColor);
  border-radius: 4px;
  background: var(--current-backgroundLight);
  color: var(--current-textPrimary);
  font-size: 0.875rem;
  
  &:focus {
    outline: none;
    border-color: var(--current-linkColor);
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
  
  &:hover {
    background: var(--current-backgroundLight);
    color: var(--current-errorColor);
  }
  
  .material-symbols-outlined {
    font-size: 1rem;
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
</style>
