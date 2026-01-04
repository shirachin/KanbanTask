<template>
  <div v-if="show" class="modal-overlay" @click.self="handleCancel">
    <div class="modal-content">
      <div class="modal-header">
        <h3>タスク追加</h3>
        <button type="button" class="modal-close" @click="handleCancel">
          <span class="material-symbols-outlined">close</span>
        </button>
      </div>
      
      <div class="modal-body">
        <div class="form-group">
          <label for="task-project">
            対象プロジェクト
            <span class="required-mark">*</span>
          </label>
          <select
            id="task-project"
            v-model="formData.project_id"
            class="form-input"
            :class="{ 'form-input-error': errors.project_id }"
            @change="handleProjectChange"
            required
          >
            <option value="">プロジェクトを選択</option>
            <option v-for="project in availableProjects" :key="project.id" :value="project.id">
              {{ project.name }}
            </option>
          </select>
          <span v-if="errors.project_id" class="error-message">{{ errors.project_id }}</span>
        </div>
        
        <div class="form-group">
          <label for="task-title">
            タスク名
            <span class="required-mark">*</span>
          </label>
          <input
            id="task-title"
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
          <label for="task-description">詳細</label>
          <textarea
            id="task-description"
            v-model="formData.description"
            class="form-input form-textarea"
            placeholder="タスクの詳細を入力"
            rows="4"
          />
        </div>
        
        <div class="form-group">
          <label for="task-status">
            フェーズ
            <span class="required-mark">*</span>
          </label>
          <select
            id="task-status"
            v-model="formData.status"
            class="form-input"
            :class="{ 'form-input-error': errors.status }"
            :disabled="!formData.project_id || loadingStatuses"
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
          <label for="task-assignee">担当者</label>
          <select
            id="task-assignee"
            v-model="formData.assignee"
            class="form-input"
          >
            <option value="">担当者を選択（任意）</option>
            <option v-for="assignee in availableAssignees" :key="assignee" :value="assignee">
              {{ assignee }}
            </option>
          </select>
        </div>
      </div>
      
      <div class="modal-footer">
        <button type="button" class="button button-cancel" @click="handleCancel">
          キャンセル
        </button>
        <button type="button" class="button button-save" @click="handleSave" :disabled="loadingStatuses">
          追加
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed, reactive } from 'vue'
import type { Project } from '../composables/useProjects'
import { DEFAULT_PERSONAL_STATUSES } from '../constants/statuses'

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
  projects: Project[]
  currentUser: string | null
}>()

const emit = defineEmits<{
  'update:show': [value: boolean]
  'save': [task: {
    project_id: number
    title: string
    description?: string | null
    status: string
    assignee?: string | null
  }]
}>()

const formData = ref({
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
  formData.value.status = '' // ステータスをリセット
  
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
      // デフォルトで「未実行」を選択（存在する場合）
      const notStartedStatus = availableStatuses.value.find((s: Status) => s.name === 'not_started')
      if (notStartedStatus) {
        formData.value.status = 'not_started'
      } else if (availableStatuses.value.length > 0) {
        formData.value.status = availableStatuses.value[0].name
      }
    } else {
      // デフォルトステータスを使用
      availableStatuses.value = DEFAULT_PERSONAL_STATUSES.map(status => ({
        ...status,
        project_id: projectId,
      }))
      formData.value.status = 'not_started' // デフォルトは「未実行」
    }
  } catch (e) {
    console.error('Error fetching statuses:', e)
    // デフォルトステータスを使用
    availableStatuses.value = DEFAULT_PERSONAL_STATUSES.map(status => ({
      ...status,
      project_id: projectId,
    }))
    formData.value.status = 'not_started' // デフォルトは「未実行」
  } finally {
    loadingStatuses.value = false
  }
}

// モーダルが開かれたときにフォームをリセット
watch(() => props.show, (newValue) => {
  if (newValue) {
    // エラーをリセット
    errors.project_id = ''
    errors.title = ''
    errors.status = ''
    
    // フォームをリセット
    formData.value = {
      project_id: '',
      title: '',
      description: '',
      status: '',
      assignee: props.currentUser || '',
    }
    availableStatuses.value = []
  }
})

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
</style>
