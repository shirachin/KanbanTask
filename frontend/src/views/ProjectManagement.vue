<template>
  <div class="project-management">
    <div class="project-header">
      <h2>プロジェクト管理</h2>
    </div>
    
    <div class="project-content">
      <AgGridVue
        ref="gridRef"
        :rowModelType="'infinite'"
        :columnDefs="columnDefs"
        :defaultColDef="defaultColDef"
        :cacheBlockSize="25"
        :maxBlocksInCache="10"
        @gridReady="onGridReady"
        class="ag-theme-quartz project-grid"
        style="width: 100%; height: 100%;"
      />
    </div>
    
    <ProjectEditModal
      v-model:show="showEditModal"
      :project="editingProject"
      @save="handleSaveProject"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, defineComponent, h } from 'vue'
import { AgGridVue } from 'ag-grid-vue3'
import type { ICellRendererParams, IDatasource, IGetRowsParams } from 'ag-grid-community'
import ProjectEditModal from '../components/ProjectEditModal.vue'
import { useProjects, type Project } from '../composables/useProjects'
import { handleApiError } from '../utils/apiClient'
import 'ag-grid-community/styles/ag-grid.css'
import 'ag-grid-community/styles/ag-theme-quartz.css'

// API composableを使用
const { fetchProjects, createProject, updateProject, deleteProject, error } = useProjects()

// AG Gridの参照
const gridRef = ref<InstanceType<typeof AgGridVue> | null>(null)

// モーダルの表示状態
const showEditModal = ref(false)
const editingProject = ref<Project | null>(null)

// カラム名のマッピング（フロントエンド → バックエンド）
const columnNameMap: Record<string, string> = {
  'id': 'id',
  'name': 'name',
  'startMonth': 'start_month',
  'endMonth': 'end_month',
  'created_at': 'created_at',
  'updated_at': 'updated_at',
}

// Infinite Scroll用のdatasource（ソート・フィルタ対応）
const createDatasource = (): IDatasource => {
  return {
    getRows: async (params: IGetRowsParams) => {
      console.log('getRows', { startRow: params.startRow, endRow: params.endRow, sortModel: params.sortModel, filterModel: params.filterModel })
      
      try {
        // ソート情報を取得
        let sortBy: string | undefined = undefined
        let sortOrder: 'asc' | 'desc' = 'desc'
        
        if (params.sortModel && params.sortModel.length > 0) {
          const firstSort = params.sortModel[0]
          sortBy = columnNameMap[firstSort.colId] || firstSort.colId
          sortOrder = firstSort.sort
          console.log('getRows: Using sort', { colId: firstSort.colId, sortBy, sortOrder })
        } else {
          // デフォルトのソート（created_at desc）
          sortBy = 'created_at'
          sortOrder = 'desc'
        }
        
        // フィルタ情報を取得
        const filters: { name?: string; startMonth?: string; endMonth?: string } = {}
        if (params.filterModel) {
          // nameフィルタ
          if (params.filterModel.name) {
            const nameFilter = params.filterModel.name
            if (nameFilter.filterType === 'text' && nameFilter.type === 'contains') {
              filters.name = nameFilter.filter
            }
          }
          // startMonthフィルタ
          if (params.filterModel.startMonth) {
            const startMonthFilter = params.filterModel.startMonth
            if (startMonthFilter.filterType === 'text' && startMonthFilter.type === 'equals') {
              filters.startMonth = startMonthFilter.filter
            }
          }
          // endMonthフィルタ
          if (params.filterModel.endMonth) {
            const endMonthFilter = params.filterModel.endMonth
            if (endMonthFilter.filterType === 'text' && endMonthFilter.type === 'equals') {
              filters.endMonth = endMonthFilter.filter
            }
          }
        }
        
        const skip = params.startRow
        const limit = params.endRow - params.startRow
        
        const result = await fetchProjects(undefined, skip, limit, sortBy, sortOrder, filters)
        
        const rowData = result.items.map((p: Project) => ({
            id: p.id,
            name: p.name,
            startMonth: p.startMonth || '',
            endMonth: p.endMonth || '',
            assignee: p.assignee || [],
          }))
        
        const lastRow = result.items.length < limit 
          ? skip + result.items.length
          : undefined
        
        params.successCallback(rowData, lastRow)
      } catch (e) {
        console.error('getRows error', e)
        params.failCallback()
      }
    },
  }
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
    // Infinite Scrollでは、データを再読み込みするためにキャッシュをリフレッシュ
    if (gridRef.value?.api && typeof gridRef.value.api.refreshInfiniteCache === 'function') {
      gridRef.value.api.refreshInfiniteCache()
    }
  } catch (e) {
    console.error('Error saving project:', e)
    alert(error.value || 'プロジェクトの保存に失敗しました')
  }
}

// プロジェクトを削除する関数（ButtonCellRendererから呼び出される）
const handleDeleteProject = async (projectId: number) => {
  try {
    await deleteProject(projectId)
    // Infinite Scrollでは、データを再読み込みするためにキャッシュをリフレッシュ
    if (gridRef.value?.api && typeof gridRef.value.api.refreshInfiniteCache === 'function') {
      gridRef.value.api.refreshInfiniteCache()
    }
  } catch (e) {
    console.error('Error deleting project:', e)
    alert(error.value || 'プロジェクトの削除に失敗しました')
  }
}

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

// Column Definitions
const columnDefs = ref([
  {
    headerName: '',
    cellRenderer: ButtonCellRenderer,
    width: 150,
    sortable: false,
    filter: false,
    resizable: false,
  },
  { field: 'name', headerName: 'プロジェクト名', flex: 1 },
  { field: 'startMonth', headerName: '開始月', width: 200 },
  { field: 'endMonth', headerName: '終了月', width: 200 },
])

// Default Column Definitions（フィルタ対応）
const defaultColDef = ref({
  sortable: true,
  resizable: true,
  filter: 'agTextColumnFilter',
  floatingFilter: true,
})

// Grid Readyイベントハンドラー（最小構成）
const onGridReady = (params: any) => {
  console.log('onGridReady')
  params.api.setGridOption('datasource', createDatasource())
}
</script>

<style lang="scss" scoped>
@import '../styles/_theme';

.project-management {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 1rem;
}

.project-header {
  margin-bottom: 1rem;
  flex-shrink: 0;

  h2 {
    margin: 0;
    font-size: 2rem;
    font-weight: 600;
  }
}

.project-content {
  flex: 1;
  min-height: 0;
}

.project-grid {
  height: 100%;
}

// ボタンセルレンダラーのスタイル
:deep(.button-cell) {
  display: flex;
  gap: 0.375rem;
  align-items: center;
  justify-content: center;
  padding: 0.125rem;
  height: 100%;
  width: 100%;
  box-sizing: border-box;

  .edit-button,
  .delete-button {
    padding: 0.25rem 0.5rem;
    border: 1px solid var(--current-borderColor);
    border-radius: 4px;
    background: var(--current-buttonBackground);
    color: var(--current-textPrimary);
    cursor: pointer;
    font-size: 0.8125rem;
    line-height: 1.2;
    transition: background-color 0.2s, border-color 0.2s;
    white-space: nowrap;
    flex-shrink: 0;
    min-width: fit-content;

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
