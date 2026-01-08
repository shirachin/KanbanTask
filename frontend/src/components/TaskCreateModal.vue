<template>
  <v-dialog
    :model-value="show"
    @update:model-value="emit('update:show', $event)"
    max-width="600"
    persistent
  >
    <v-card>
      <v-card-title class="d-flex justify-space-between align-center">
        <span>タスク追加</span>
        <v-btn
          icon="mdi-close"
          variant="text"
          size="small"
          @click="handleCancel"
        />
      </v-card-title>

      <v-divider />

      <v-card-text>
        <v-form ref="formRef">
          <v-autocomplete
            v-model="selectedProjectId"
            :items="availableProjects"
            item-title="name"
            item-value="id"
            label="対象プロジェクト"
            :rules="[rules.required]"
            :error-messages="errors.project_id ? [errors.project_id] : []"
            @update:model-value="handleProjectChange"
            class="mb-4"
          />

          <v-text-field
            v-model="formData.title"
            label="タスク名"
            :rules="[rules.required]"
            :error-messages="errors.title ? [errors.title] : []"
            placeholder="タスク名を入力"
            class="mb-4"
          />

          <v-textarea
            v-model="formData.description"
            label="詳細"
            placeholder="タスクの詳細を入力"
            rows="4"
            class="mb-4"
          />

          <v-select
            v-model="formData.status"
            :items="availableStatuses"
            item-title="display_name"
            item-value="name"
            label="フェーズ"
            :rules="[rules.required]"
            :error-messages="errors.status ? [errors.status] : []"
            :disabled="!formData.project_id || loadingStatuses"
            :loading="loadingStatuses"
            class="mb-4"
          >
            <template v-slot:no-data>
              <v-list-item>
                <v-list-item-title>フェーズを選択</v-list-item-title>
              </v-list-item>
            </template>
          </v-select>

          <v-select
            v-model="formData.assignee"
            :items="availableAssignees"
            label="担当者"
            placeholder="担当者を選択（任意）"
            clearable
          />
        </v-form>
      </v-card-text>

      <v-divider />

      <v-card-actions>
        <v-spacer />
        <v-btn
          variant="text"
          @click="handleCancel"
        >
          キャンセル
        </v-btn>
        <v-btn
          color="primary"
          @click="handleSave"
          :disabled="loadingStatuses"
        >
          追加
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, watch, computed, reactive } from 'vue'
import type { Project } from '../composables/useProjects'
import { useStatuses, type Status } from '../composables/useStatuses'
import { DEFAULT_PERSONAL_STATUSES } from '../constants/statuses'

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

const formRef = ref()
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

const rules = {
  required: (value: any) => !!value || '必須項目です',
}

const { statuses: statusesData, fetchStatuses: fetchStatusesData } = useStatuses()
const loadingStatuses = ref(false)
const availableStatuses = ref<Status[]>([])
const selectedProjectId = ref<number | null>(null)

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
  
  const projectId = selectedProjectId.value
  if (projectId !== null) {
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
const handleProjectChange = async (projectId: number | null = null) => {
  const id = projectId !== null ? projectId : selectedProjectId.value
  formData.value.project_id = id !== null ? id.toString() : ''
  formData.value.status = '' // ステータスをリセット
  
  if (id === null) {
    availableStatuses.value = []
    return
  }
  
  loadingStatuses.value = true
  
  try {
    await fetchStatusesData()
    if (statusesData.value && statusesData.value.length > 0) {
      availableStatuses.value = statusesData.value.sort((a: Status, b: Status) => (a.order || 0) - (b.order || 0))
      // デフォルトで「未実行」を選択（存在する場合）
      const notStartedStatus = availableStatuses.value.find((s: Status) => s.name === 'not_started')
      if (notStartedStatus) {
        formData.value.status = 'not_started'
      } else if (availableStatuses.value.length > 0) {
        formData.value.status = availableStatuses.value[0].name
      }
    } else {
      // デフォルトステータスを使用（フォールバック）
      availableStatuses.value = DEFAULT_PERSONAL_STATUSES.map(status => ({
        id: 0,
        name: status.name,
        display_name: status.display_name,
        order: status.order,
        color: status.color,
        project_id: null,
      }))
      formData.value.status = 'not_started' // デフォルトは「未実行」
    }
  } catch (e) {
    console.error('Error fetching statuses:', e)
    // デフォルトステータスを使用（フォールバック）
    availableStatuses.value = DEFAULT_PERSONAL_STATUSES.map(status => ({
      id: 0,
      name: status.name,
      display_name: status.display_name,
      order: status.order,
      color: status.color,
      project_id: null,
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
    selectedProjectId.value = null
    
    // フォームのバリデーションをリセット
    if (formRef.value) {
      formRef.value.reset()
    }
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
  if (!selectedProjectId.value) {
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

const handleSave = async () => {
  // フォームのバリデーション
  if (formRef.value) {
    const { valid } = await formRef.value.validate()
    if (!valid) {
      return
    }
  }
  
  // カスタムバリデーション
  if (!validateForm()) {
    return
  }
  
  if (!selectedProjectId.value) {
    return
  }
  
  emit('save', {
    project_id: selectedProjectId.value,
    title: formData.value.title.trim(),
    description: formData.value.description.trim() || null,
    status: formData.value.status,
    assignee: formData.value.assignee || (selectedProjectId.value === -1 ? props.currentUser : null),
  })
  emit('update:show', false)
}
</script>

<style lang="scss" scoped>
// Vuetifyコンポーネントを使用するため、カスタムスタイルは最小限に
</style>
