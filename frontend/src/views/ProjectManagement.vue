<template>
  <div class="project-management">
    <div class="project-header">
      <h2>プロジェクト管理</h2>
    </div>
    
    <div class="project-content">
      <div v-if="error" class="error-message">
        {{ error }}
      </div>
      <div class="project-section">
        <div class="section-header">
          <h3 class="section-title">プロジェクト一覧</h3>
          <button type="button" class="add-project-button" @click="openAddModal" :disabled="loading">
            <span class="material-symbols-outlined">add</span>
            プロジェクト追加
          </button>
        </div>
        <div v-if="loading && rowData.length === 0" class="loading-message">
          読み込み中...
        </div>
        <AgGridVue
          v-else
          :rowData="rowData"
          :columnDefs="columnDefs"
          :defaultColDef="defaultColDef"
          class="ag-theme-quartz"
          style="height: 500px; width: 100%;"
        />
      </div>
    </div>
    
    <ProjectEditModal
      v-model:show="showEditModal"
      :project="editingProject"
      @save="handleSaveProject"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, defineComponent, h, onMounted, watch } from 'vue'
import { AgGridVue } from 'ag-grid-vue3'
import type { ICellRendererParams } from 'ag-grid-community'
import AssigneeCellRenderer from '../components/AssigneeCellRenderer.vue'
import ProjectEditModal from '../components/ProjectEditModal.vue'
import { useProjects, type Project } from '../composables/useProjects'
import 'ag-grid-community/styles/ag-grid.css'
import 'ag-grid-community/styles/ag-theme-quartz.css'

// API composableを使用
const { projects, loading, error, fetchProjects, createProject, updateProject, deleteProject } = useProjects()

// モーダルの表示状態
const showEditModal = ref(false)
const editingProject = ref<Project | null>(null)

// AG Grid用のrowData（projectsを変換）
const rowData = ref<Project[]>([])

// projectsが変更されたらrowDataを更新
const updateRowData = () => {
  rowData.value = projects.value.map((p: Project) => ({
    id: p.id,
    name: p.name,
    startMonth: p.startMonth || '',
    endMonth: p.endMonth || '',
    assignee: p.assignee || [],
  }))
}

// プロジェクトを監視してrowDataを更新
watch(projects, updateRowData, { deep: true })

// 新規追加モーダルを開く関数
const openAddModal = () => {
  editingProject.value = {
    id: 0, // 新規作成時は0
    name: '',
    startMonth: '',
    endMonth: '',
    assignee: [''],
  }
  showEditModal.value = true
}

// 編集モーダルを開く関数
const openEditModal = (project: Project) => {
  editingProject.value = { ...project }
  showEditModal.value = true
}

// プロジェクトを保存する関数
const handleSaveProject = async (project: Project) => {
  try {
    if (project.id === 0) {
      // 新規作成
      await createProject({
        name: project.name,
        startMonth: project.startMonth,
        endMonth: project.endMonth,
        assignee: project.assignee,
      })
    } else {
      // 更新
      await updateProject(project.id, {
        name: project.name,
        startMonth: project.startMonth,
        endMonth: project.endMonth,
        assignee: project.assignee,
      })
    }
    updateRowData()
  } catch (e) {
    console.error('Error saving project:', e)
    alert(error.value || 'プロジェクトの保存に失敗しました')
  }
}

// プロジェクトを削除する関数（ButtonCellRendererから呼び出される）
const handleDeleteProject = async (projectId: number) => {
  try {
    await deleteProject(projectId)
    updateRowData()
  } catch (e) {
    console.error('Error deleting project:', e)
    alert(error.value || 'プロジェクトの削除に失敗しました')
  }
}

// 初期データを読み込む
onMounted(async () => {
  await fetchProjects()
  updateRowData()
})

// ボタンセルレンダラーコンポーネント
const ButtonCellRenderer = defineComponent({
  props: {
    params: {
      type: Object as () => ICellRendererParams,
      required: true,
    },
  },
  setup(props: { params: ICellRendererParams }) {
    const handleEdit = () => {
      const projectData = props.params.data as Project | undefined
      if (projectData) {
        openEditModal(projectData)
      }
    }

    const handleDelete = () => {
      const projectName = props.params.data?.name || '不明'
      const projectId = props.params.data?.id
      
      if (!projectId) {
        alert('プロジェクトIDが見つかりません。')
        return
      }
      
      if (confirm(`「${projectName}」を削除しますか？`)) {
        handleDeleteProject(projectId)
      }
    }

    return () => h('div', { class: 'button-cell' }, [
      h('button', {
        class: 'edit-button',
        onClick: handleEdit,
      }, '編集'),
      h('button', {
        class: 'delete-button',
        onClick: handleDelete,
      }, '削除'),
    ])
  },
})

// Column Definitions: Defines the columns to be displayed.
const columnDefs = ref([
  {
    headerName: 'ボタン',
    cellRenderer: ButtonCellRenderer,
    width: 150,
    sortable: false,
    filter: false,
    resizable: false,
  },
  { field: 'name', headerName: 'プロジェクト名', flex: 1 },
  { field: 'startMonth', headerName: '開始月', width: 120 },
  { field: 'endMonth', headerName: '終了月', width: 120 },
  { 
    field: 'assignee',
    headerName: '担当者', 
    width: 200,
    cellRenderer: AssigneeCellRenderer,
    autoHeight: true,
    wrapText: false,
    valueFormatter: (params: any) => {
      // 警告を回避するためのフォーマッター（実際の表示はcellRendererで行う）
      const assignees = Array.isArray(params.value) ? params.value : params.value ? [params.value] : []
      return assignees.join(', ')
    },
  },
])

// Default Column Definitions
const defaultColDef = ref({
  sortable: true,
  filter: true,
  resizable: true,
})
</script>

<style lang="scss" scoped>
@import '../styles/_theme';

.project-management {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.project-header {
  margin-bottom: 2rem;

  h2 {
    margin: 0;
    color: var(--current-textPrimary);
    font-size: 2rem;
    font-weight: 600;
  }
}

.project-content {
  background: var(--current-backgroundLight);
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 8px var(--current-shadowMd);
}

.project-section {
  margin-bottom: 2rem;

  &:last-child {
    margin-bottom: 0;
  }
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.section-title {
  margin: 0;
  color: var(--current-textPrimary);
  font-size: 1.25rem;
  font-weight: 600;
}

.add-project-button {
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

  &:hover {
    background: var(--current-linkColor);
    border-color: var(--current-linkColor);
  }

  &:active {
    transform: scale(0.98);
  }

  .material-symbols-outlined {
    font-size: 1.25rem;
  }
}

.project-list {
  min-height: 200px;
}

.empty-message {
  margin: 0;
  color: var(--current-textSecondary);
  font-size: 0.875rem;
  text-align: center;
  padding: 2rem 0;
}

.error-message {
  background: #f8d7da;
  color: #721c24;
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1rem;
  border: 1px solid #f5c6cb;
}

.loading-message {
  text-align: center;
  padding: 2rem;
  color: var(--current-textSecondary);
  font-size: 1rem;
}

.add-project-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

// ボタンセルレンダラーのスタイル
:deep(.button-cell) {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  justify-content: center;
  padding: 0.25rem;

  .edit-button,
  .delete-button {
    padding: 0.375rem 0.75rem;
    border: 1px solid var(--current-borderColor);
    border-radius: 4px;
    background: var(--current-buttonBackground);
    color: var(--current-textPrimary);
    cursor: pointer;
    font-size: 0.875rem;
    transition: background-color 0.2s, border-color 0.2s;

    &:hover {
      background: var(--current-buttonHoverBackground);
      border-color: var(--current-buttonHoverBorderColor);
    }

    &:active {
      background: var(--current-activeBackground);
      color: var(--current-textWhite);
    }
  }

  .delete-button {
    background: var(--current-backgroundLight);
    color: #dc3545;

    &:hover {
      background: #f8d7da;
      border-color: #dc3545;
    }

    &:active {
      background: #dc3545;
      color: white;
    }
  }
}
</style>
