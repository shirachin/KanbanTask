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
          ref="gridRef"
          :rowData="rowData"
          :columnDefs="columnDefs"
          :defaultColDef="defaultColDef"
          :pagination="true"
          :paginationPageSize="paginationPageSize"
          :paginationPageSizeSelector="[25, 50, 100, 200]"
          @columnStateChanged="onColumnStateChanged"
          @filterChanged="onFilterChanged"
          @paginationChanged="onPaginationChanged"
          @sortChanged="onSortChanged"
          @firstDataRendered="onFirstDataRendered"
          @gridReady="onGridReady"
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
import { ref, defineComponent, h, onMounted, watch, nextTick } from 'vue'
import { AgGridVue } from 'ag-grid-vue3'
import type { ICellRendererParams, ColumnState, FilterModel } from 'ag-grid-community'
import AssigneeCellRenderer from '../components/AssigneeCellRenderer.vue'
import ProjectEditModal from '../components/ProjectEditModal.vue'
import { useProjects, type Project } from '../composables/useProjects'
import { getLocalStorage, setLocalStorage, STORAGE_KEYS } from '../composables/useLocalStorage'
import 'ag-grid-community/styles/ag-grid.css'
import 'ag-grid-community/styles/ag-theme-quartz.css'

// API composableを使用
const { projects, loading, error, fetchProjects, createProject, updateProject, deleteProject } = useProjects()

// AG Gridの参照
const gridRef = ref<InstanceType<typeof AgGridVue> | null>(null)

// ページネーションサイズ
const savedPageSize = getLocalStorage<number>(STORAGE_KEYS.PROJECT_MANAGEMENT_PAGE_SIZE, 50)
const paginationPageSize = ref<number>([25, 50, 100, 200].includes(savedPageSize) ? savedPageSize : 50)

// 初期化フラグ（初期化時のイベントを無視するため）
const isInitializing = ref(true)

// カラム状態（ソート、表示/非表示、幅など）
const savedColumnState = getLocalStorage<ColumnState[]>(STORAGE_KEYS.PROJECT_MANAGEMENT_COLUMN_STATE, [])
const columnState = ref<ColumnState[]>(savedColumnState)

// ソートモデル（ソート状態を保存するため）
interface SortModel {
  colId: string
  sort: 'asc' | 'desc'
}
const savedSortModel = getLocalStorage<SortModel[]>(STORAGE_KEYS.PROJECT_MANAGEMENT_COLUMN_STATE + '_sort', [])
const sortModel = ref<SortModel[]>(savedSortModel)

// フィルタモデル
const savedFilterModel = getLocalStorage<FilterModel>(STORAGE_KEYS.PROJECT_MANAGEMENT_FILTER_MODEL, {})
const filterModel = ref<FilterModel>(savedFilterModel)

// モーダルの表示状態
const showEditModal = ref(false)
const editingProject = ref<Project | null>(null)

// AG Grid用のrowData（projectsを変換）
const rowData = ref<Project[]>([])

// projectsが変更されたらrowDataを更新（システム用プロジェクト（id=-1）は除外）
const updateRowData = () => {
  rowData.value = projects.value
    .filter((p: Project) => p.id !== -1)  // システム用プロジェクト（id=-1）を除外
    .map((p: Project) => ({
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
  // データが読み込まれた後に状態を復元
  await nextTick()
  if (gridRef.value?.api && rowData.value.length > 0) {
    if (!hasRestoredState) {
      restoreGridState()
    }
  }
})

// データが更新された時に状態を復元（初回のみ）
watch(rowData, async (newData) => {
  if (newData.length > 0 && !hasRestoredState && gridRef.value?.api) {
    await nextTick()
    restoreGridState()
  }
}, { immediate: false })

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
  filter: 'agTextColumnFilter',
  resizable: true,
  floatingFilter: false,
})

// カラム状態変更時の処理
const onColumnStateChanged = () => {
  if (!gridRef.value?.api || isInitializing.value) return
  
  const state = gridRef.value.api.getColumnState()
  const relevantState = state.map((col: any) => ({
    colId: col.colId,
    sort: col.sort,
    sortIndex: col.sortIndex,
    width: col.width,
    hide: col.hide,
  }))
  
  columnState.value = relevantState
  setLocalStorage(STORAGE_KEYS.PROJECT_MANAGEMENT_COLUMN_STATE, relevantState.length > 0 ? relevantState : null)
  
  // ソートモデルも別途保存
  const columnStateForSort = gridRef.value.api.getColumnState()
  const sortFromState = columnStateForSort
    .filter((col: any) => col.sort)
    .sort((a: any, b: any) => (a.sortIndex || 0) - (b.sortIndex || 0))
    .map((col: any) => ({ colId: col.colId, sort: col.sort }))
  
  if (sortFromState.length > 0) {
    sortModel.value = sortFromState
    setLocalStorage(STORAGE_KEYS.PROJECT_MANAGEMENT_COLUMN_STATE + '_sort', sortFromState)
  } else {
    sortModel.value = []
    setLocalStorage(STORAGE_KEYS.PROJECT_MANAGEMENT_COLUMN_STATE + '_sort', null)
  }
}

// ソート変更時の処理
const onSortChanged = () => {
  if (!gridRef.value?.api || isInitializing.value) return
  
  const columnStateForSort = gridRef.value.api.getColumnState()
  const sortFromState = columnStateForSort
    .filter((col: any) => col.sort)
    .sort((a: any, b: any) => (a.sortIndex || 0) - (b.sortIndex || 0))
    .map((col: any) => ({ colId: col.colId, sort: col.sort }))
  
  if (sortFromState.length > 0) {
    sortModel.value = sortFromState
    setLocalStorage(STORAGE_KEYS.PROJECT_MANAGEMENT_COLUMN_STATE + '_sort', sortFromState)
  } else {
    sortModel.value = []
    setLocalStorage(STORAGE_KEYS.PROJECT_MANAGEMENT_COLUMN_STATE + '_sort', null)
  }
}

// フィルタ変更時の処理
const onFilterChanged = () => {
  if (!gridRef.value?.api || isInitializing.value) return
  
  const model = gridRef.value.api.getFilterModel()
  filterModel.value = model
  setLocalStorage(STORAGE_KEYS.PROJECT_MANAGEMENT_FILTER_MODEL, Object.keys(model).length > 0 ? model : null)
}

// ページネーション変更時の処理
const onPaginationChanged = () => {
  if (!gridRef.value?.api || isInitializing.value) return
  
  let pageSize: number
  if (typeof gridRef.value.api.paginationGetPageSize === 'function') {
    pageSize = gridRef.value.api.paginationGetPageSize()
  } else if (typeof gridRef.value.api.getGridOption === 'function') {
    pageSize = gridRef.value.api.getGridOption('paginationPageSize') || 50
  } else {
    return
  }
  
  if (paginationPageSize.value !== pageSize) {
    paginationPageSize.value = pageSize
    setLocalStorage(STORAGE_KEYS.PROJECT_MANAGEMENT_PAGE_SIZE, pageSize)
  }
}

// 状態復元フラグ
let hasRestoredState = false
let retryCount = 0
const MAX_RETRY_COUNT = 50

// 状態を復元する関数
const restoreGridState = () => {
  if (!gridRef.value || hasRestoredState) return
  
  if (retryCount >= MAX_RETRY_COUNT) {
    isInitializing.value = false
    return
  }
  
  const api = gridRef.value.api
  if (!api) {
    retryCount++
    setTimeout(() => {
      if (!hasRestoredState && gridRef.value) {
        restoreGridState()
      }
    }, 100)
    return
  }
  
  const hasPaginationMethod = typeof api.paginationSetPageSize === 'function' || 
                              typeof api.setGridOption === 'function'
  const hasColumnStateMethod = typeof api.applyColumnState === 'function' || 
                               typeof api.setGridOption === 'function'
  const hasFilterMethod = typeof api.setFilterModel === 'function' || 
                          typeof api.setGridOption === 'function'
  
  if (!hasPaginationMethod || !hasColumnStateMethod || !hasFilterMethod) {
    retryCount++
    setTimeout(() => {
      if (!hasRestoredState && gridRef.value) {
        restoreGridState()
      }
    }, 100)
    return
  }
  
  isInitializing.value = true
  retryCount = 0
  
  try {
    // ページサイズを復元
    const pageSizeValue = paginationPageSize.value
    if (typeof api.setGridOption === 'function') {
      api.setGridOption('paginationPageSize', pageSizeValue)
    }
    
    // ソートモデルを復元
    if (sortModel.value.length > 0) {
      const sortColumnState = sortModel.value.map((sort: any, index: number) => ({
        colId: sort.colId,
        sort: sort.sort,
        sortIndex: index,
      }))
      
      if (typeof api.applyColumnState === 'function') {
        api.applyColumnState({ 
          state: sortColumnState,
          applyOrder: false
        })
      }
    } else if (columnState.value.length > 0) {
      const sortFromState = columnState.value
        .filter((col: any) => col.sort)
        .sort((a: any, b: any) => (a.sortIndex || 0) - (b.sortIndex || 0))
        .map((col: any) => ({ 
          colId: col.colId, 
          sort: col.sort,
          sortIndex: col.sortIndex || 0
        }))
      
      if (sortFromState.length > 0 && typeof api.applyColumnState === 'function') {
        api.applyColumnState({ 
          state: sortFromState,
          applyOrder: false
        })
      }
    }
    
    // カラム状態を復元（幅や表示/非表示など、ソートは除外）
    if (columnState.value.length > 0) {
      if (typeof api.applyColumnState === 'function') {
        const stateWithoutSort = columnState.value.map((col: any) => ({
          ...col,
          sort: undefined,
          sortIndex: undefined,
        }))
        api.applyColumnState({ 
          state: stateWithoutSort,
          applyOrder: true
        })
      }
    }
    
    // フィルタモデルを復元
    if (Object.keys(filterModel.value).length > 0) {
      if (typeof api.setFilterModel === 'function') {
        api.setFilterModel(filterModel.value)
      }
    }
    
    hasRestoredState = true
  } catch (e) {
    console.error('Error restoring grid state:', e)
  } finally {
    setTimeout(() => {
      isInitializing.value = false
    }, 200)
  }
}

// Grid Readyイベントハンドラー
const onGridReady = () => {
  if (!hasRestoredState && rowData.value.length > 0) {
    setTimeout(() => {
      if (!hasRestoredState) {
        restoreGridState()
      }
    }, 300)
  }
}

// 最初のデータレンダリング後の処理
const onFirstDataRendered = () => {
  if (!hasRestoredState) {
    setTimeout(() => {
      if (!hasRestoredState) {
        restoreGridState()
      }
    }, 500)
  }
}
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
  background: var(--current-errorBackground);
  color: var(--current-errorText);
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1rem;
  border: 1px solid var(--current-errorBorder);
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
    color: var(--current-errorColor);

    &:hover {
      background: var(--current-errorBackground);
      border-color: var(--current-errorColor);
    }

    &:active {
      background: var(--current-errorColor);
      color: var(--current-textWhite);
    }
  }
}
</style>
