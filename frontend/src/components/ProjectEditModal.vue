<template>
  <div v-if="show" class="modal-overlay" @click.self="handleCancel">
    <div class="modal-content">
      <div class="modal-header">
        <h3>{{ isNewProject ? 'プロジェクト追加' : 'プロジェクト編集' }}</h3>
        <button type="button" class="modal-close" @click="handleCancel">
          <span class="material-symbols-outlined">close</span>
        </button>
      </div>
      
      <div class="modal-body">
        <div class="form-group">
          <label for="project-name">
            プロジェクト名
            <span class="required-mark">*</span>
          </label>
          <input
            id="project-name"
            v-model="formData.name"
            type="text"
            class="form-input"
            :class="{ 'form-input-error': errors.name }"
            placeholder="プロジェクト名を入力"
            required
          />
          <span v-if="errors.name" class="error-message">{{ errors.name }}</span>
        </div>
        
        <div class="form-group">
          <label for="start-month">
            開始月
            <span class="required-mark">*</span>
          </label>
          <input
            id="start-month"
            v-model="formData.startMonth"
            type="month"
            class="form-input"
            :class="{ 'form-input-error': errors.startMonth }"
            required
          />
          <span v-if="errors.startMonth" class="error-message">{{ errors.startMonth }}</span>
        </div>
        
        <div class="form-group">
          <label for="end-month">終了月</label>
          <input
            id="end-month"
            v-model="formData.endMonth"
            type="month"
            class="form-input"
          />
        </div>
        
        <div class="form-group">
          <label>
            担当者
            <span class="required-mark">*</span>
          </label>
          <div class="assignee-input-container">
            <div v-for="(assignee, index) in formData.assignee" :key="index" class="assignee-input-row">
              <input
                v-model="formData.assignee[index]"
                type="text"
                class="form-input assignee-input"
                placeholder="担当者名を入力"
              />
              <button
                type="button"
                class="remove-assignee-button"
                @click="removeAssignee(index)"
                :disabled="formData.assignee.length === 1"
              >
                <span class="material-symbols-outlined">delete</span>
              </button>
            </div>
            <button type="button" class="add-assignee-button" @click="addAssignee">
              <span class="material-symbols-outlined">add</span>
              担当者を追加
            </button>
            <span v-if="errors.assignee" class="error-message">{{ errors.assignee }}</span>
          </div>
        </div>
      </div>
      
      <div class="modal-footer">
        <button type="button" class="button button-cancel" @click="handleCancel">
          キャンセル
        </button>
        <button type="button" class="button button-save" @click="handleSave">
          保存
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed, reactive } from 'vue'

type Project = {
  id: number
  name: string
  startMonth: string
  endMonth: string
  assignee: string[]
}

const props = defineProps<{
  show: boolean
  project: Project | null
}>()

const emit = defineEmits<{
  (e: 'update:show', value: boolean): void
  (e: 'save', project: Project): void
}>()

const formData = ref<Project>({
  id: 0,
  name: '',
  startMonth: '',
  endMonth: '',
  assignee: [''],
})

const errors = reactive({
  name: '',
  startMonth: '',
  assignee: '',
})

const isNewProject = computed(() => {
  return props.project?.id === 0 || !props.project
})

watch(
  () => props.project,
  (newProject) => {
    // エラーをリセット
    errors.name = ''
    errors.startMonth = ''
    errors.assignee = ''
    
    if (newProject) {
      formData.value = {
        id: newProject.id,
        name: newProject.name,
        startMonth: newProject.startMonth,
        endMonth: newProject.endMonth,
        assignee: newProject.assignee.length > 0 ? [...newProject.assignee] : [''],
      }
    } else {
      formData.value = {
        id: 0,
        name: '',
        startMonth: '',
        endMonth: '',
        assignee: [''],
      }
    }
  },
  { immediate: true }
)

const handleCancel = () => {
  emit('update:show', false)
}

const validateForm = (): boolean => {
  // エラーをリセット
  errors.name = ''
  errors.startMonth = ''
  errors.assignee = ''
  
  let isValid = true
  
  // プロジェクト名のバリデーション
  if (!formData.value.name.trim()) {
    errors.name = 'プロジェクト名は必須です。'
    isValid = false
  }
  
  // 開始月のバリデーション
  if (!formData.value.startMonth) {
    errors.startMonth = '開始月は必須です。'
    isValid = false
  }
  
  // 担当者のバリデーション
  const validAssignees = formData.value.assignee.filter((a) => a.trim() !== '')
  if (validAssignees.length === 0) {
    errors.assignee = '担当者を1人以上入力してください。'
    isValid = false
  }
  
  return isValid
}

const handleSave = () => {
  if (!validateForm()) {
    return
  }
  
  // 空の担当者を除外
  const validAssignees = formData.value.assignee.filter((a) => a.trim() !== '')
  
  emit('save', {
    ...formData.value,
    assignee: validAssignees,
  })
  emit('update:show', false)
}

const addAssignee = () => {
  formData.value.assignee.push('')
}

const removeAssignee = (index: number) => {
  if (formData.value.assignee.length > 1) {
    formData.value.assignee.splice(index, 1)
  }
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
  box-shadow: 0 4px 16px var(--current-shadowLg);
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

  .modal-close {
    padding: 0.5rem;
    border: none;
    background: transparent;
    color: var(--current-textSecondary);
    cursor: pointer;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background-color 0.2s, color 0.2s;

    &:hover {
      background: var(--current-hoverBackground);
      color: var(--current-textPrimary);
    }

    .material-symbols-outlined {
      font-size: 1.5rem;
    }
  }
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  flex: 1;
}

.form-group {
  margin-bottom: 1.5rem;

  label {
    display: block;
    margin-bottom: 0.5rem;
    color: var(--current-textPrimary);
    font-size: 0.875rem;
    font-weight: 500;

    .required-mark {
      color: var(--current-errorColor);
      margin-left: 0.25rem;
    }
  }
}

.form-input {
  width: 100%;
  padding: 0.625rem 0.75rem;
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

  &.form-input-error {
    border-color: var(--current-errorColor);
  }
}

.error-message {
  display: block;
  margin-top: 0.25rem;
  color: var(--current-errorColor);
  font-size: 0.75rem;
}

.assignee-input-container {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.assignee-input-row {
  display: flex;
  gap: 0.5rem;
  align-items: center;

  .assignee-input {
    flex: 1;
  }

  .remove-assignee-button {
    padding: 0.625rem;
    border: 1px solid var(--current-borderColor);
    border-radius: 4px;
    background: var(--current-backgroundLight);
    color: var(--current-errorColor);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background-color 0.2s;
    flex-shrink: 0;

    &:hover:not(:disabled) {
      background: var(--current-errorBackground);
    }

    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }

    .material-symbols-outlined {
      font-size: 1.25rem;
    }
  }
}

.add-assignee-button {
  padding: 0.625rem 0.75rem;
  border: 1px dashed var(--current-borderColor);
  border-radius: 4px;
  background: transparent;
  color: var(--current-textPrimary);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  transition: border-color 0.2s, background-color 0.2s;

  &:hover {
    border-color: var(--current-linkColor);
    background: var(--current-hoverBackground);
  }

  .material-symbols-outlined {
    font-size: 1.25rem;
  }
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1.5rem;
  border-top: 1px solid var(--current-borderColor);
}

.button {
  padding: 0.625rem 1.25rem;
  border: 1px solid var(--current-borderColor);
  border-radius: 4px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s, border-color 0.2s, color 0.2s;

  &.button-cancel {
    background: var(--current-backgroundLight);
    color: var(--current-textPrimary);

    &:hover {
      background: var(--current-hoverBackground);
    }
  }

  &.button-save {
    background: var(--current-activeBackground);
    color: var(--current-textWhite);
    border-color: var(--current-activeBackground);

    &:hover {
      background: var(--current-linkColor);
      border-color: var(--current-linkColor);
    }
  }
}
</style>
